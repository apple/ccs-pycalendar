##
#    Copyright (c) 2007-2013 Cyrus Daboo. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##

from pycalendar import stringutils, xmlutils, xmldefinitions
from pycalendar.parameter import Parameter
from pycalendar.binaryvalue import BinaryValue
from pycalendar.caladdressvalue import CalAddressValue
from pycalendar.datetimevalue import DateTimeValue
from pycalendar.durationvalue import DurationValue
from pycalendar.exceptions import InvalidProperty
from pycalendar.integervalue import IntegerValue
from pycalendar.multivalue import MultiValue
from pycalendar.periodvalue import PeriodValue
from pycalendar.plaintextvalue import PlainTextValue
from pycalendar.unknownvalue import UnknownValue
from pycalendar.urivalue import URIValue
from pycalendar.utcoffsetvalue import UTCOffsetValue
from pycalendar.utils import decodeParameterValue
from pycalendar.value import Value
import cStringIO as StringIO
import xml.etree.cElementTree as XML

class PropertyBase(object):

    # Mappings between various tokens and internal definitions
    sDefaultValueTypeMap = {}
    sValueTypeMap = {}
    sTypeValueMap = {}
    sMultiValues = set()
    sSpecialVariants = {}

    sUsesGroup = False

    sVariant = "none"   # Used to differentiate different forms of text parsing

    sValue = None
    sText = None

    def __init__(self, name=None, value=None, valuetype=None):
        raise NotImplementedError


    def duplicate(self):
        raise NotImplementedError


    def __hash__(self):
        raise NotImplementedError


    def __ne__(self, other):
        return not self.__eq__(other)


    def __eq__(self, other):
        raise NotImplementedError


    def __repr__(self):
        return "Property: %s" % (self.getText(),)


    def __str__(self):
        return self.getText()


    def getGroup(self):
        return self.mGroup if self.sUsesGroup else None


    def setGroup(self, group):
        if self.sUsesGroup:
            self.mGroup = group


    def getName(self):
        return self.mName


    def setName(self, name):
        self.mName = name


    def getParameters(self):
        return self.mParameters


    def setParameters(self, parameters):
        self.mParameters = dict([(k.upper(), v) for k, v in parameters.iteritems()])


    def hasParameter(self, attr):
        return attr.upper() in self.mParameters


    def getParameterValue(self, attr):
        return self.mParameters[attr.upper()][0].getFirstValue()


    def addParameter(self, attr):
        self.mParameters.setdefault(attr.getName().upper(), []).append(attr)


    def replaceParameter(self, attr):
        self.mParameters[attr.getName().upper()] = [attr]


    def removeParameters(self, attr):
        if attr.upper() in self.mParameters:
            del self.mParameters[attr.upper()]


    def getValue(self):
        return self.mValue


    def getBinaryValue(self):

        if isinstance(self.mValue, BinaryValue):
            return self.mValue
        else:
            return None


    def getCalAddressValue(self):

        if isinstance(self.mValue, CalAddressValue):
            return self.mValue
        else:
            return None


    def getDateTimeValue(self):

        if isinstance(self.mValue, DateTimeValue):
            return self.mValue
        else:
            return None


    def getDurationValue(self):

        if isinstance(self.mValue, DurationValue):
            return self.mValue
        else:
            return None


    def getIntegerValue(self):

        if isinstance(self.mValue, IntegerValue):
            return self.mValue
        else:
            return None


    def getMultiValue(self):

        if isinstance(self.mValue, MultiValue):
            return self.mValue
        else:
            return None


    def getPeriodValue(self):

        if isinstance(self.mValue, PeriodValue):
            return self.mValue
        else:
            return None


    def getTextValue(self):

        if isinstance(self.mValue, PlainTextValue):
            return self.mValue
        else:
            return None


    def getURIValue(self):

        if isinstance(self.mValue, URIValue):
            return self.mValue
        else:
            return None


    def getUTCOffsetValue(self):

        if isinstance(self.mValue, UTCOffsetValue):
            return self.mValue
        else:
            return None


    @classmethod
    def parseText(cls, data):
        """
        Parse the text format data and return a L{Property}

        @param data: text data
        @type data: C{str}
        """

        try:
            prop = cls()

            # Look for parameter or value delimiter
            prop_name, txt = stringutils.strduptokenstr(data, ";:")
            if not prop_name:
                raise InvalidProperty("Invalid property", data)

            # Get the name
            if prop.sUsesGroup:
                # Check for group prefix
                splits = prop_name.split(".", 1)
                if len(splits) == 2:
                    # We have both group and name
                    prop.mGroup = splits[0]
                    prop.mName = splits[1]
                else:
                    # We have the name
                    prop.mName = prop_name
            else:
                prop.mName = prop_name

            # Get the parameters
            txt = prop.parseTextParameters(txt, data)

            # Tidy first
            prop.mValue = None

            # Get value type from property name
            value_type = prop.determineValueType()

            # Check for multivalued
            if prop.mName.upper() in prop.sMultiValues:
                prop.mValue = MultiValue(value_type)
            else:
                # Create the type
                prop.mValue = Value.createFromType(value_type)

            # Now parse the data
            prop.mValue.parse(txt, prop.sVariant)

            prop._postCreateValue(value_type)

            return prop

        except Exception:
            raise InvalidProperty("Invalid property", data)


    def parseTextParameters(self, txt, data):
        """
        Parse parameters, return string point at value.
        """

        try:
            while txt:
                if txt[0] == ';':
                    # Parse parameter

                    # Move past delimiter
                    txt = txt[1:]

                    # Get quoted string or token
                    parameter_name, txt = stringutils.strduptokenstr(txt, "=")
                    if parameter_name is None:
                        raise InvalidProperty("Invalid property", data)
                    txt = txt[1:]
                    parameter_value, txt = stringutils.strduptokenstr(txt, ":;,")
                    if parameter_value is None:
                        raise InvalidProperty("Invalid property", data)

                    # Now add parameter value (decode ^-escaping)
                    attrvalue = Parameter(name=parameter_name, value=decodeParameterValue(parameter_value))
                    self.mParameters.setdefault(parameter_name.upper(), []).append(attrvalue)

                    # Look for additional values
                    while txt[0] == ',':
                        txt = txt[1:]
                        parameter_value2, txt = stringutils.strduptokenstr(txt, ":;,")
                        if parameter_value2 is None:
                            raise InvalidProperty("Invalid property", data)
                        attrvalue.addValue(decodeParameterValue(parameter_value2))
                elif txt[0] == ':':
                    return txt[1:]
                else:
                    # We should never get here but if we do we need to terminate the loop
                    raise InvalidProperty("Invalid property", data)

        except IndexError:
            raise InvalidProperty("Invalid property", data)


    def getText(self):
        os = StringIO.StringIO()
        self.generate(os)
        return os.getvalue()


    def generate(self, os):

        # Write it out always with value
        self.generateValue(os, False)


    def generateFiltered(self, os, filter):

        # Check for property in filter and whether value is written out
        test, novalue = filter.testPropertyValue(self.mName.upper())
        if test:
            self.generateValue(os, novalue)


    # Write out the actual property, possibly skipping the value
    def generateValue(self, os, novalue):

        self.setupValueParameter()

        # Must write to temp buffer and then wrap
        sout = StringIO.StringIO()
        if self.sUsesGroup and self.mGroup:
            sout.write(self.mGroup + ".")
        sout.write(self.mName)

        # Write all parameters
        for key in sorted(self.mParameters.keys()):
            for attr in self.mParameters[key]:
                sout.write(";")
                attr.generate(sout)

        # Write value
        sout.write(":")
        if self.mValue and not novalue:
            self.mValue.generate(sout)

        # Get string text
        temp = sout.getvalue()
        sout.close()

        # Look for line length exceed
        if len(temp) < 75:
            os.write(temp)
        else:
            # Look for valid utf8 range and write that out
            start = 0
            written = 0
            lineWrap = 74
            while written < len(temp):
                # Start 74 chars on from where we are
                offset = start + lineWrap
                if offset >= len(temp):
                    line = temp[start:]
                    os.write(line)
                    written = len(temp)
                else:
                    # Check whether next char is valid utf8 lead byte
                    while (temp[offset] > 0x7F) and ((ord(temp[offset]) & 0xC0) == 0x80):
                        # Step back until we have a valid char
                        offset -= 1

                    line = temp[start:offset]
                    os.write(line)
                    os.write("\r\n ")
                    lineWrap = 73   # We are now adding a space at the start
                    written += offset - start
                    start = offset

        os.write("\r\n")


    def writeXML(self, node, namespace):

        # Write it out always with value
        self.generateValueXML(node, namespace, False)


    def writeXMLFiltered(self, node, namespace, filter):

        # Check for property in filter and whether value is written out
        test, novalue = filter.testPropertyValue(self.mName.upper())
        if test:
            self.generateValueXML(node, namespace, novalue)


    # Write out the actual property, possibly skipping the value
    def generateValueXML(self, node, namespace, novalue):

        prop = XML.SubElement(node, xmlutils.makeTag(namespace, self.getName()))

        # Write all parameters
        if len(self.mParameters):
            params = XML.SubElement(prop, xmlutils.makeTag(namespace, xmldefinitions.parameters))
            for key in sorted(self.mParameters.keys()):
                for attr in self.mParameters[key]:
                    if attr.getName().lower() != "value":
                        attr.writeXML(params, namespace)

        # Write value
        if self.mValue and not novalue:
            self.mValue.writeXML(prop, namespace)


    @classmethod
    def parseJSON(cls, jobject):
        """
        Parse a JSON property of the form:

        [name, attrs, type, value1, value2, ...]

        @param jobject: a JSON array
        @type jobject: C{list}
        """

        try:
            prop = cls()

            # Get the name
            prop.mName = jobject[0].upper()

            # Get the parameters
            if jobject[1]:
                for name, value in jobject[1].items():
                    # Now add parameter value
                    name = name.upper()
                    attrvalue = Parameter(name=name, value=value)
                    prop.mParameters.setdefault(name, []).append(attrvalue)

            # Get default value type from property name and insert a VALUE parameter if current value type is not default
            value_type = cls.sValueTypeMap.get(jobject[2].upper(), Value.VALUETYPE_UNKNOWN)
            default_type = cls.sDefaultValueTypeMap.get(prop.mName.upper(), Value.VALUETYPE_UNKNOWN)
            if default_type != value_type:
                attrvalue = Parameter(name=cls.sValue, value=jobject[2].upper())
                prop.mParameters.setdefault(cls.sValue, []).append(attrvalue)

            # Get value type from property name
            value_type = prop.determineValueType()

            # Check for multivalued
            values = jobject[3:]
            if prop.mName.upper() in cls.sMultiValues:
                prop.mValue = MultiValue(value_type)
                prop.mValue.parseJSONValue(values)
            else:
                # Create the type
                prop.mValue = Value.createFromType(value_type)
                prop.mValue.parseJSONValue(values[0])

            # Special post-create for some types
            prop._postCreateValue(value_type)

            return prop

        except Exception:
            raise InvalidProperty("Invalid property", jobject)


    def writeJSON(self, jobject):

        # Write it out always with value
        self.generateValueJSON(jobject, False)


    def writeJSONFiltered(self, jobject, filter):

        # Check for property in filter and whether value is written out
        test, novalue = filter.testPropertyValue(self.mName.upper())
        if test:
            self.generateValueJSON(jobject, novalue)


    def generateValueJSON(self, jobject, novalue):

        prop = [
            self.getName().lower(),
            {},
        ]
        jobject.append(prop)

        # Write all parameters
        for key in sorted(self.mParameters.keys()):
            for attr in self.mParameters[key]:
                if attr.getName().lower() != "value":
                    attr.writeJSON(prop[1])

        # Write value
        if self.mValue and not novalue:
            self.mValue.writeJSON(prop)


    def determineValueType(self):
        # Get value type from property name
        value_type = self.sDefaultValueTypeMap.get(self.mName.upper(), Value.VALUETYPE_UNKNOWN)

        # Check whether custom value is set
        if self.sValue in self.mParameters:
            attr = self.getParameterValue(self.sValue)
            if attr != self.sText:
                value_type = self.sValueTypeMap.get(attr, value_type)

        # Check for specials
        if self.mName.upper() in self.sSpecialVariants:
            # Make sure we have the default value for the special
            if value_type == self.sDefaultValueTypeMap.get(self.mName.upper(), Value.VALUETYPE_UNKNOWN):
                value_type = self.sSpecialVariants[self.mName.upper()]

        return value_type


    def createValue(self, data):
        # Tidy first
        self.mValue = None

        # Get value type from property name
        value_type = self.determineValueType()

        # Check for multivalued
        if self.mName.upper() in self.sMultiValues:
            self.mValue = MultiValue(value_type)
        else:
            # Create the type
            self.mValue = Value.createFromType(value_type)

        # Now parse the data
        try:
            self.mValue.parse(data, self.sVariant)
        except ValueError:
            raise InvalidProperty("Invalid property value", data)

        self._postCreateValue(value_type)


    def _postCreateValue(self, value_type):
        """
        Do some extra work after creating a value in this property.

        @param value_type: the iCalendar VALUE type for this property
        @type value_type: C{str}
        """
        pass


    def setValue(self, value):
        # Tidy first
        self.mValue = None

        # Get value type from property name
        value_type = self.sDefaultValueTypeMap.get(self.mName.upper(), Value.VALUETYPE_TEXT)

        # Check whether custom value is set
        if self.sValue in self.mParameters:
            value_type = self.sValueTypeMap.get(self.getParameterValue(self.sValue), value_type)

        # Check for multivalued
        if self.mName.upper() in self.sMultiValues:
            self.mValue = MultiValue(value_type)
        else:
            # Create the type
            self.mValue = Value.createFromType(value_type)

        self.mValue.setValue(value)

        # Special post-create for some types
        self._postCreateValue(value_type)


    def setupValueParameter(self):
        if self.sValue in self.mParameters:
            del self.mParameters[self.sValue]

        # Only if we have a value right now
        if self.mValue is None:
            return

        # See if current type is default for this property. If there is no mapping available,
        # then always add VALUE if it is not TEXT.
        default_type = self.sDefaultValueTypeMap.get(self.mName.upper())
        if self.mName.upper() in self.sSpecialVariants:
            actual_type = default_type
        else:
            actual_type = self.mValue.getType()
        if default_type is None or default_type != actual_type:
            actual_value = self.sTypeValueMap.get(actual_type)
            if actual_value is not None and (default_type is not None or actual_type != Value.VALUETYPE_TEXT):
                self.mParameters.setdefault(self.sValue, []).append(Parameter(name=self.sValue, value=actual_value))


    # Creation
    def _init_attr_value_int(self, ival):
        # Value
        self.mValue = IntegerValue(value=ival)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_text(self, txt, value_type):
        # Value
        self.mValue = Value.createFromType(value_type)
        if isinstance(self.mValue, PlainTextValue) or isinstance(self.mValue, UnknownValue):
            self.mValue.setValue(txt)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_datetime(self, dt):
        # Value
        self.mValue = DateTimeValue(value=dt)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_utcoffset(self, utcoffset):
        # Value
        self.mValue = UTCOffsetValue()
        self.mValue.setValue(utcoffset.getValue())

        # Parameters
        self.setupValueParameter()
