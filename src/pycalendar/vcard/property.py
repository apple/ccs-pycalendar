##
#    Copyright (c) 2007-2011 Cyrus Daboo. All rights reserved.
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

from pycalendar import stringutils
from pycalendar.adr import Adr
from pycalendar.adrvalue import AdrValue
from pycalendar.attribute import PyCalendarAttribute
from pycalendar.datetime import PyCalendarDateTime
from pycalendar.datetimevalue import PyCalendarDateTimeValue
from pycalendar.dummyvalue import PyCalendarDummyValue
from pycalendar.exceptions import PyCalendarInvalidProperty
from pycalendar.integervalue import PyCalendarIntegerValue
from pycalendar.multivalue import PyCalendarMultiValue
from pycalendar.n import N
from pycalendar.nvalue import NValue
from pycalendar.orgvalue import OrgValue
from pycalendar.parser import ParserContext
from pycalendar.plaintextvalue import PyCalendarPlainTextValue
from pycalendar.utcoffsetvalue import PyCalendarUTCOffsetValue
from pycalendar.value import PyCalendarValue
from pycalendar.vcard import definitions
import cStringIO as StringIO

handleOptions = ("allow", "ignore", "fix", "raise")
missingParameterValues = "fix"

class Property(object):

    sDefaultValueTypeMap = {
    
        #     2425 Properties
        definitions.Property_SOURCE  : PyCalendarValue.VALUETYPE_URI,
        definitions.Property_NAME    : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_PROFILE : PyCalendarValue.VALUETYPE_TEXT,
        
        #     2426 vCard Properties
        
        #     2426 Section 3.1
        definitions.Property_FN       : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_N        : PyCalendarValue.VALUETYPE_N,
        definitions.Property_NICKNAME : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_PHOTO    : PyCalendarValue.VALUETYPE_BINARY,
        definitions.Property_BDAY     : PyCalendarValue.VALUETYPE_DATE,
        
        #     2426 Section 3.2
        definitions.Property_ADR   : PyCalendarValue.VALUETYPE_ADR,
        definitions.Property_LABEL : PyCalendarValue.VALUETYPE_TEXT,
        
        #     2426 Section 3.3
        definitions.Property_TEL    : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_EMAIL  : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_MAILER : PyCalendarValue.VALUETYPE_TEXT,
        
        #     2426 Section 3.4
        definitions.Property_TZ  : PyCalendarValue.VALUETYPE_UTC_OFFSET,
        definitions.Property_GEO : PyCalendarValue.VALUETYPE_GEO,
        
        #     2426 Section 3.5
        definitions.Property_TITLE : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_ROLE  : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_LOGO  : PyCalendarValue.VALUETYPE_BINARY,
        definitions.Property_AGENT : PyCalendarValue.VALUETYPE_VCARD,
        definitions.Property_ORG   : PyCalendarValue.VALUETYPE_ORG,
        
        #     2426 Section 3.6
        definitions.Property_CATEGORIES  : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_NOTE        : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_PRODID      : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_REV         : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.Property_SORT_STRING : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_SOUND       : PyCalendarValue.VALUETYPE_BINARY,
        definitions.Property_UID         : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_URL         : PyCalendarValue.VALUETYPE_URI,
        definitions.Property_VERSION     : PyCalendarValue.VALUETYPE_TEXT,
    
        #     2426 Section 3.7
        definitions.Property_CLASS       : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Property_KEY         : PyCalendarValue.VALUETYPE_BINARY,
    }
    
    sValueTypeMap = {
        definitions.Value_BINARY      : PyCalendarValue.VALUETYPE_BINARY,
        definitions.Value_BOOLEAN     : PyCalendarValue.VALUETYPE_BOOLEAN,
        definitions.Value_DATE        : PyCalendarValue.VALUETYPE_DATE,
        definitions.Value_DATE_TIME   : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.Value_FLOAT       : PyCalendarValue.VALUETYPE_FLOAT,
        definitions.Value_INTEGER     : PyCalendarValue.VALUETYPE_INTEGER,
        definitions.Value_TEXT        : PyCalendarValue.VALUETYPE_TEXT,
        definitions.Value_TIME        : PyCalendarValue.VALUETYPE_TIME,
        definitions.Value_URI         : PyCalendarValue.VALUETYPE_URI,
        definitions.Value_UTCOFFSET   : PyCalendarValue.VALUETYPE_UTC_OFFSET,
        definitions.Value_VCARD       : PyCalendarValue.VALUETYPE_VCARD,
    }

    sTypeValueMap = {
        PyCalendarValue.VALUETYPE_ADR        : definitions.Value_TEXT,
        PyCalendarValue.VALUETYPE_BINARY     : definitions.Value_BINARY,
        PyCalendarValue.VALUETYPE_BOOLEAN    : definitions.Value_BOOLEAN,
        PyCalendarValue.VALUETYPE_DATE       : definitions.Value_DATE,
        PyCalendarValue.VALUETYPE_DATETIME   : definitions.Value_DATE_TIME,
        PyCalendarValue.VALUETYPE_FLOAT      : definitions.Value_FLOAT,
        PyCalendarValue.VALUETYPE_GEO        : definitions.Value_FLOAT,
        PyCalendarValue.VALUETYPE_INTEGER    : definitions.Value_INTEGER,
        PyCalendarValue.VALUETYPE_N          : definitions.Value_TEXT,
        PyCalendarValue.VALUETYPE_ORG        : definitions.Value_TEXT,
        PyCalendarValue.VALUETYPE_TEXT       : definitions.Value_TEXT,
        PyCalendarValue.VALUETYPE_TIME       : definitions.Value_TIME,
        PyCalendarValue.VALUETYPE_URI        : definitions.Value_URI,
        PyCalendarValue.VALUETYPE_UTC_OFFSET : definitions.Value_UTCOFFSET,
        PyCalendarValue.VALUETYPE_VCARD      : definitions.Value_VCARD,
    }

    sMultiValues = set((
        definitions.Property_NICKNAME,
        definitions.Property_CATEGORIES,
    ))

    sTextVariants = set((
        definitions.Property_ADR,
        definitions.Property_N,
        definitions.Property_ORG,
    ))

    def __init__(self, group=None, name=None, value=None, valuetype=None):
        self._init_PyCalendarProperty()

        self.mGroup = group

        self.mName = name if name is not None else ""

        if isinstance(value, int):
            self._init_attr_value_int(value)

        elif isinstance(value, str):
            self._init_attr_value_text(value, valuetype if valuetype else Property.sDefaultValueTypeMap.get(self.mName.upper(), PyCalendarValue.VALUETYPE_TEXT))

        elif isinstance(value, PyCalendarDateTime):
            self._init_attr_value_datetime(value)

        elif isinstance(value, Adr):
            self._init_attr_value_adr(value)

        elif isinstance(value, N):
            self._init_attr_value_n(value)

        elif isinstance(value, list) or isinstance(value, tuple):
            if name.upper() == definitions.Property_ORG:
                self._init_attr_value_org(value)
            elif name.upper() == definitions.Property_GEO:
                self._init_attr_value_geo(value)
            else:
                # Assume everything else is a text list
                self._init_attr_value_text_list(value)

        elif isinstance(value, PyCalendarUTCOffsetValue):
            self._init_attr_value_utcoffset(value)

    def duplicate(self):
        other = Property(self.mGroup, self.mName)
        for attrname, attrs in self.mAttributes.items():
            other.mAttributes[attrname] = [i.duplicate() for i in attrs]
        other.mValue = self.mValue.duplicate()

        return other

    def __hash__(self):
        return hash((
            self.mName,
            tuple([tuple(self.mAttributes[attrname]) for attrname in sorted(self.mAttributes.keys())]),
            self.mValue,
        ))

    def __ne__(self, other): return not self.__eq__(other)
    def __eq__(self, other):
        if not isinstance(other, Property): return False
        return (
            self.mGroup == self.mGroup and
            self.mName == other.mName and
            self.mValue == other.mValue and
            self.mAttributes == other.mAttributes
        )

    def __repr__(self):
        return "vCard Property: %s" % (self.getText(),)

    def __str__(self):
        return self.getText()

    def getGroup(self):
        return self.mGroup

    def setGroup(self, group):
        self.mGroup = group

    def getName(self):
        return self.mName

    def setName(self, name):
        self.mName = name

    def getAttributes(self):
        return self.mAttributes

    def setAttributes(self, attributes):
        self.mAttributes = dict([(k.upper(), v) for k,v in attributes.iteritems()])

    def hasAttribute(self, attr):
        return self.mAttributes.has_key(attr.upper())

    def getAttributeValue(self, attr):
        return self.mAttributes[attr.upper()][0].getFirstValue()

    def addAttribute(self, attr):
        self.mAttributes.setdefault(attr.getName().upper(), []).append(attr)

    def replaceAttribute(self, attr):
        self.mAttributes[attr.getName().upper()] = [attr]

    def removeAttributes(self, attr):
        if self.mAttributes.has_key(attr.upper()):
            del self.mAttributes[attr.upper()]

    def getValue(self):
        return self.mValue

    def parse(self, data):
        # Look for attribute or value delimiter
        prop_name, txt = stringutils.strduptokenstr(data, ";:")
        if not prop_name:
            raise PyCalendarInvalidProperty("Invalid property", data)

        # Check for group prefix
        splits = prop_name.split(".", 1)
        if len(splits) == 2:
            # We have both group and name
            self.mGroup = splits[0]
            self.mName = splits[1]
        else:
            # We have the name
            self.mName = prop_name
        
        # Now loop getting data
        try:
            stripValueSpaces = False    # Fix for AB.app base PHOTO properties that use two spaces at start of line
            while txt:
                if txt[0] == ';':
                    # Parse attribute
    
                    # Move past delimiter
                    txt = txt[1:]
    
                    # Get quoted string or token - in iCalendar we only look for "=" here
                    # but for "broken" vCard BASE64 property we need to also terminate on
                    # ":;" 
                    attribute_name, txt = stringutils.strduptokenstr(txt, "=:;")
                    if attribute_name is None:
                        raise PyCalendarInvalidProperty("Invalid property", data)
                    
                    if txt[0] != "=":
                        # Deal with parameters without values
                        if ParserContext.VCARD_2_NO_PARAMETER_VALUES == ParserContext.PARSER_RAISE:
                            raise PyCalendarInvalidProperty("Invalid property parameter", data)
                        elif ParserContext.VCARD_2_NO_PARAMETER_VALUES == ParserContext.PARSER_ALLOW:
                            attribute_value = None
                        else: # PARSER_IGNORE and PARSER_FIX
                            attribute_name = None

                        if attribute_name.upper() == "BASE64" and ParserContext.VCARD_2_BASE64 == ParserContext.PARSER_FIX:
                            attribute_name = definitions.Parameter_ENCODING
                            attribute_value = definitions.Parameter_Value_ENCODING_B
                            stripValueSpaces = True
                    else:
                        txt = txt[1:]
                        attribute_value, txt = stringutils.strduptokenstr(txt, ":;,")
                        if attribute_value is None:
                            raise PyCalendarInvalidProperty("Invalid property", data)
    
                    # Now add attribute value
                    if attribute_name is not None:
                        attrvalue = PyCalendarAttribute(name = attribute_name, value=attribute_value)
                        self.mAttributes.setdefault(attribute_name.upper(), []).append(attrvalue)
    
                    # Look for additional values
                    while txt[0] == ',':
                        txt = txt[1:]
                        attribute_value2, txt = stringutils.strduptokenstr(txt, ":;,")
                        if attribute_value2 is None:
                            raise PyCalendarInvalidProperty("Invalid property", data)
                        attrvalue.addValue(attribute_value2)
                elif txt[0] == ':':
                    txt = txt[1:]
                    if stripValueSpaces:
                        txt = txt.replace(" ", "")
                    self.createValue(txt)
                    txt = None

        except IndexError:
            raise PyCalendarInvalidProperty("Invalid property", data)
            
        # We must have a value of some kind
        if self.mValue is None:
            raise PyCalendarInvalidProperty("Invalid property", data)
        
        return True


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

        self.setupValueAttribute()

        # Must write to temp buffer and then wrap
        sout = StringIO.StringIO()
        if self.mGroup:
            sout.write(self.mGroup + ".")
        sout.write(self.mName)

        # Write all attributes
        for key in sorted(self.mAttributes.keys()):
            for attr in self.mAttributes[key]:
                sout.write(";")
                attr.generate(sout)

        # Write value
        sout.write(":")
        if self.mName.upper() == "PHOTO" and self.mValue.getType() == PyCalendarValue.VALUETYPE_BINARY:
            # Handle AB.app PHOTO values
            sout.write("\r\n")
            
            value = self.mValue.getText()
            value_len = len(value)
            offset = 0
            while(value_len > 72):
                sout.write(" ")
                sout.write(value[offset:offset+72])
                sout.write("\r\n")
                value_len -= 72
                offset += 72
            sout.write(" ")
            sout.write(value[offset:])
            os.write(sout.getvalue())
        else:
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
    
    def _init_PyCalendarProperty(self):
        self.mGroup = None
        self.mName = ""
        self.mAttributes = {}
        self.mValue = None

    def createValue(self, data):
        # Tidy first
        self.mValue = None

        # Get value type from property name
        valueType = Property.sDefaultValueTypeMap.get(self.mName.upper(), PyCalendarValue.VALUETYPE_TEXT)

        # Check whether custom value is set
        if self.mAttributes.has_key(definitions.Parameter_VALUE):
            attr = self.getAttributeValue(definitions.Parameter_VALUE)
            if attr != definitions.Value_TEXT or self.mName.upper() not in Property.sTextVariants:
                valueType = Property.sValueTypeMap.get(attr, valueType)

        # Check for multivalued
        if self.mName.upper() in Property.sMultiValues:
            self.mValue = PyCalendarMultiValue(valueType)
        else:
            # Create the type
            self.mValue = PyCalendarValue.createFromType(valueType)

        # Now parse the data
        try:
            if valueType in (PyCalendarValue.VALUETYPE_DATE, PyCalendarValue.VALUETYPE_DATETIME):
                # vCard supports a slightly different, expanded form, of date
                self.mValue.parse(data, fullISO=True)
            else:
                self.mValue.parse(data)
        except ValueError:
            raise PyCalendarInvalidProperty("Invalid property value", data)

    def setValue(self, value):
        # Tidy first
        self.mValue = None

        # Get value type from property name
        valueType = Property.sDefaultValueTypeMap.get(self.mName.upper(), PyCalendarDummyValue)

        # Check whether custom value is set
        if self.mAttributes.has_key(definitions.Parameter_VALUE):
            attr = self.getAttributeValue(definitions.Parameter_VALUE)
            if attr != definitions.Value_TEXT or self.mName.upper() not in Property.sTextVariants:
                valueType = Property.sValueTypeMap.get(attr, valueType)

        # Check for multivalued
        if self.mName.upper() in Property.sMultiValues:
            self.mValue = PyCalendarMultiValue(valueType)
        else:
            # Create the type
            self.mValue = PyCalendarValue.createFromType(valueType)

        self.mValue.setValue(value)

    def setupValueAttribute(self):
        if self.mAttributes.has_key(definitions.Parameter_VALUE):
            del self.mAttributes[definitions.Parameter_VALUE]

        # Only if we have a value right now
        if self.mValue is None:
            return

        # See if current type is default for this property
        default_type = Property.sDefaultValueTypeMap.get(self.mName.upper())
        if default_type is not None:
            actual_type = self.mValue.getType()
            if default_type != actual_type:
                actual_value = self.sTypeValueMap.get(actual_type)
                if actual_value is not None:
                    self.mAttributes.setdefault(definitions.Parameter_VALUE, []).append(PyCalendarAttribute(name=definitions.Parameter_VALUE, value=actual_value))

    # Creation
    def _init_attr_value_int(self, ival):
        # Value
        self.mValue = PyCalendarIntegerValue(value=ival)

        # Attributes
        self.setupValueAttribute()


    def _init_attr_value_text(self, txt, value_type):
        # Value
        self.mValue = PyCalendarValue.createFromType(value_type)
        if isinstance(self.mValue, PyCalendarPlainTextValue) or isinstance(self.mValue, PyCalendarDummyValue):
            self.mValue.setValue(txt)

        # Attributes
        self.setupValueAttribute()

    def _init_attr_value_adr(self, reqstatus):
        # Value
        self.mValue = AdrValue(reqstatus)

        # Attributes
        self.setupValueAttribute()

    def _init_attr_value_n(self, reqstatus):
        # Value
        self.mValue = NValue(reqstatus)

        # Attributes
        self.setupValueAttribute()

    def _init_attr_value_org(self, reqstatus):
        # Value
        self.mValue = OrgValue(reqstatus)

        # Attributes
        self.setupValueAttribute()

    def _init_attr_value_datetime(self, dt):
        # Value
        self.mValue = PyCalendarDateTimeValue(value=dt)

        # Attributes
        self.setupValueAttribute()
    
    def _init_attr_value_utcoffset(self, utcoffset):
        # Value
        self.mValue = PyCalendarUTCOffsetValue()
        self.mValue.setValue(utcoffset.getValue())

        # Attributes
        self.setupValueAttribute()

