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

from pycalendar import definitions
from pycalendar import stringutils
from pycalendar.attribute import PyCalendarAttribute
from pycalendar.binaryvalue import PyCalendarBinaryValue
from pycalendar.caladdressvalue import PyCalendarCalAddressValue
from pycalendar.datetime import PyCalendarDateTime
from pycalendar.datetimevalue import PyCalendarDateTimeValue
from pycalendar.dummyvalue import PyCalendarDummyValue
from pycalendar.duration import PyCalendarDuration
from pycalendar.durationvalue import PyCalendarDurationValue
from pycalendar.exceptions import PyCalendarInvalidProperty
from pycalendar.integervalue import PyCalendarIntegerValue
from pycalendar.multivalue import PyCalendarMultiValue
from pycalendar.period import PyCalendarPeriod
from pycalendar.periodvalue import PyCalendarPeriodValue
from pycalendar.plaintextvalue import PyCalendarPlainTextValue
from pycalendar.recurrence import PyCalendarRecurrence
from pycalendar.recurrencevalue import PyCalendarRecurrenceValue
from pycalendar.requeststatusvalue import PyCalendarRequestStatusValue
from pycalendar.urivalue import PyCalendarURIValue
from pycalendar.utcoffsetvalue import PyCalendarUTCOffsetValue
from pycalendar.value import PyCalendarValue
import cStringIO as StringIO

class PyCalendarProperty(object):

    sDefaultValueTypeMap = {

        # 2445 ?4.8.1
        definitions.cICalProperty_ATTACH           : PyCalendarValue.VALUETYPE_URI,
        definitions.cICalProperty_CATEGORIES       : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_CLASS            : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_COMMENT          : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_DESCRIPTION      : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_GEO              : PyCalendarValue.VALUETYPE_GEO,
        definitions.cICalProperty_LOCATION         : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_PERCENT_COMPLETE : PyCalendarValue.VALUETYPE_INTEGER,
        definitions.cICalProperty_PRIORITY         : PyCalendarValue.VALUETYPE_INTEGER,
        definitions.cICalProperty_RESOURCES        : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_STATUS           : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_SUMMARY          : PyCalendarValue.VALUETYPE_TEXT,

        # 2445 ?4.8.2
        definitions.cICalProperty_COMPLETED : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_DTEND     : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_DUE       : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_DTSTART   : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_DURATION  : PyCalendarValue.VALUETYPE_DURATION,
        definitions.cICalProperty_FREEBUSY  : PyCalendarValue.VALUETYPE_PERIOD,
        definitions.cICalProperty_TRANSP    : PyCalendarValue.VALUETYPE_TEXT,

        # 2445 ?4.8.3
        definitions.cICalProperty_TZID         : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_TZNAME       : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_TZOFFSETFROM : PyCalendarValue.VALUETYPE_UTC_OFFSET,
        definitions.cICalProperty_TZOFFSETTO   : PyCalendarValue.VALUETYPE_UTC_OFFSET,
        definitions.cICalProperty_TZURL        : PyCalendarValue.VALUETYPE_URI,

        # 2445 ?4.8.4
        definitions.cICalProperty_ATTENDEE      : PyCalendarValue.VALUETYPE_CALADDRESS,
        definitions.cICalProperty_CONTACT       : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_ORGANIZER     : PyCalendarValue.VALUETYPE_CALADDRESS,
        definitions.cICalProperty_RECURRENCE_ID : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_RELATED_TO    : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_URL           : PyCalendarValue.VALUETYPE_URI,
        definitions.cICalProperty_UID           : PyCalendarValue.VALUETYPE_TEXT,

        # 2445 ?4.8.5
        definitions.cICalProperty_EXDATE : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_EXRULE : PyCalendarValue.VALUETYPE_RECUR,
        definitions.cICalProperty_RDATE  : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_RRULE  : PyCalendarValue.VALUETYPE_RECUR,

        # 2445 ?4.8.6
        definitions.cICalProperty_ACTION  : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_REPEAT  : PyCalendarValue.VALUETYPE_INTEGER,
        definitions.cICalProperty_TRIGGER : PyCalendarValue.VALUETYPE_DURATION,

        # 2445 ?4.8.7
        definitions.cICalProperty_CREATED       : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_DTSTAMP       : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_LAST_MODIFIED : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_SEQUENCE      : PyCalendarValue.VALUETYPE_INTEGER,

        # 2445 ?4.8.8
        definitions.cICalProperty_REQUEST_STATUS : PyCalendarValue.VALUETYPE_REQUEST_STATUS,

        # Apple Extensions
        definitions.cICalProperty_XWRCALNAME : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_XWRCALDESC : PyCalendarValue.VALUETYPE_TEXT,

        # Mulberry extensions
        definitions.cICalProperty_ACTION_X_SPEAKTEXT  : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalProperty_ALARM_X_LASTTRIGGER : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalProperty_ALARM_X_ALARMSTATUS : PyCalendarValue.VALUETYPE_TEXT,
    }

    sValueTypeMap = {

        # 2445 ?4.3
        definitions.cICalValue_BINARY      : PyCalendarValue.VALUETYPE_BINARY,
        definitions.cICalValue_BOOLEAN     : PyCalendarValue.VALUETYPE_BOOLEAN,
        definitions.cICalValue_CAL_ADDRESS : PyCalendarValue.VALUETYPE_CALADDRESS,
        definitions.cICalValue_DATE        : PyCalendarValue.VALUETYPE_DATE,
        definitions.cICalValue_DATE_TIME   : PyCalendarValue.VALUETYPE_DATETIME,
        definitions.cICalValue_DURATION    : PyCalendarValue.VALUETYPE_DURATION,
        definitions.cICalValue_FLOAT       : PyCalendarValue.VALUETYPE_FLOAT,
        definitions.cICalValue_INTEGER     : PyCalendarValue.VALUETYPE_INTEGER,
        definitions.cICalValue_PERIOD      : PyCalendarValue.VALUETYPE_PERIOD,
        definitions.cICalValue_RECUR       : PyCalendarValue.VALUETYPE_RECUR,
        definitions.cICalValue_TEXT        : PyCalendarValue.VALUETYPE_TEXT,
        definitions.cICalValue_TIME        : PyCalendarValue.VALUETYPE_TIME,
        definitions.cICalValue_URI         : PyCalendarValue.VALUETYPE_URI,
        definitions.cICalValue_UTC_OFFSET  : PyCalendarValue.VALUETYPE_UTC_OFFSET,
    }

    sTypeValueMap = {

        # 2445 ?4.3
        PyCalendarValue.VALUETYPE_BINARY         : definitions.cICalValue_BINARY,
        PyCalendarValue.VALUETYPE_BOOLEAN        : definitions.cICalValue_BOOLEAN,
        PyCalendarValue.VALUETYPE_CALADDRESS     : definitions.cICalValue_CAL_ADDRESS,
        PyCalendarValue.VALUETYPE_DATE           : definitions.cICalValue_DATE,
        PyCalendarValue.VALUETYPE_DATETIME       : definitions.cICalValue_DATE_TIME,
        PyCalendarValue.VALUETYPE_DURATION       : definitions.cICalValue_DURATION,
        PyCalendarValue.VALUETYPE_FLOAT          : definitions.cICalValue_FLOAT,
        PyCalendarValue.VALUETYPE_GEO            : definitions.cICalValue_FLOAT,
        PyCalendarValue.VALUETYPE_INTEGER        : definitions.cICalValue_INTEGER,
        PyCalendarValue.VALUETYPE_PERIOD         : definitions.cICalValue_PERIOD,
        PyCalendarValue.VALUETYPE_RECUR          : definitions.cICalValue_RECUR,
        PyCalendarValue.VALUETYPE_TEXT           : definitions.cICalValue_TEXT,
        PyCalendarValue.VALUETYPE_REQUEST_STATUS : definitions.cICalValue_TEXT,
        PyCalendarValue.VALUETYPE_TIME           : definitions.cICalValue_TIME,
        PyCalendarValue.VALUETYPE_URI            : definitions.cICalValue_URI,
        PyCalendarValue.VALUETYPE_UTC_OFFSET     : definitions.cICalValue_UTC_OFFSET,
    }

    sMultiValues = set((
        definitions.cICalProperty_CATEGORIES,
        definitions.cICalProperty_RESOURCES,
        definitions.cICalProperty_FREEBUSY,
        definitions.cICalProperty_EXDATE,
        definitions.cICalProperty_RDATE,
    ))

    def __init__(self, name = None, value = None, valuetype = None):
        self._init_PyCalendarProperty()
        self.mName = name if name is not None else ""

        if isinstance(value, int):
            self._init_attr_value_int(value)

        elif isinstance(value, str):
            self._init_attr_value_text(value, valuetype if valuetype else PyCalendarProperty.sDefaultValueTypeMap.get(self.mName.upper(), PyCalendarValue.VALUETYPE_TEXT))

        elif isinstance(value, PyCalendarDateTime):
            self._init_attr_value_datetime(value)

        elif isinstance(value, list):
            if name.upper() == definitions.cICalProperty_REQUEST_STATUS:
                self._init_attr_value_requeststatus(value)
            else:
                period_list = False
                if len(value) != 0:
                    period_list = isinstance(value[0], PyCalendarPeriod)
                if period_list:
                    self._init_attr_value_periodlist(value)
                else:
                    self._init_attr_value_datetimelist(value)

        elif isinstance(value, PyCalendarDuration):
            self._init_attr_value_duration(value)

        elif isinstance(value, PyCalendarPeriod):
            self._init_attr_value_period(value)

        elif isinstance(value, PyCalendarRecurrence):
            self._init_attr_value_recur(value)

        elif isinstance(value, PyCalendarUTCOffsetValue):
            self._init_attr_value_utcoffset(value)

    def duplicate(self):
        other = PyCalendarProperty(self.mName)
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
        if not isinstance(other, PyCalendarProperty): return False
        return self.mName == other.mName and self.mValue == other.mValue and self.mAttributes == other.mAttributes

    def __repr__(self):
        return "PyCalendarProperty: %s" % (self.getText(),)

    def __str__(self):
        return self.getText()

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

    def getBinaryValue(self):

        if isinstance(self.mValue, PyCalendarBinaryValue):
            return self.mValue
        else:
            return None

    def getCalAddressValue(self):

        if isinstance(self.mValue, PyCalendarCalAddressValue):
            return self.mValue
        else:
            return None

    def getDateTimeValue(self):

        if isinstance(self.mValue, PyCalendarDateTimeValue):
            return self.mValue
        else:
            return None

    def getDurationValue(self):

        if isinstance(self.mValue, PyCalendarDurationValue):
            return self.mValue
        else:
            return None

    def getIntegerValue(self):

        if isinstance(self.mValue, PyCalendarIntegerValue):
            return self.mValue
        else:
            return None

    def getMultiValue(self):

        if isinstance(self.mValue, PyCalendarMultiValue):
            return self.mValue
        else:
            return None

    def getPeriodValue(self):

        if isinstance(self.mValue, PyCalendarPeriodValue):
            return self.mValue
        else:
            return None

    def getRecurrenceValue(self):

        if isinstance(self.mValue, PyCalendarRecurrenceValue):
            return self.mValue
        else:
            return None

    def getTextValue(self):

        if isinstance(self.mValue, PyCalendarPlainTextValue):
            return self.mValue
        else:
            return None

    def getURIValue(self):

        if isinstance(self.mValue, PyCalendarURIValue):
            return self.mValue
        else:
            return None

    def getUTCOffsetValue(self):

        if isinstance(self.mValue, PyCalendarUTCOffsetValue):
            return self.mValue
        else:
            return None

    def parse(self, data):
        # Look for attribute or value delimiter
        prop_name, txt = stringutils.strduptokenstr(data, ";:")
        if not prop_name:
            raise PyCalendarInvalidProperty("Invalid property", data)

        # We have the name
        self.mName = prop_name
        
        # TODO: Try to use static string for the name

        # Now loop getting data
        try:
            while txt:
                if txt[0] == ';':
                    # Parse attribute
    
                    # Move past delimiter
                    txt = txt[1:]
    
                    # Get quoted string or token
                    attribute_name, txt = stringutils.strduptokenstr(txt, "=")
                    if attribute_name is None:
                        raise PyCalendarInvalidProperty("Invalid property", data)
                    txt = txt[1:]
                    attribute_value, txt = stringutils.strduptokenstr(txt, ":;,")
                    if attribute_value is None:
                        raise PyCalendarInvalidProperty("Invalid property", data)
    
                    # Now add attribute value
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
        sout.write(self.mName)

        # Write all attributes
        for key in sorted(self.mAttributes.keys()):
            for attr in self.mAttributes[key]:
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
            while written < len(temp):
                # Start 74 chars on from where we are
                offset = start + 74
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
                    written += offset - start
                    start = offset
    
        os.write("\r\n")
    
    def _init_PyCalendarProperty(self):
        self.mName = ""
        self.mAttributes = {}
        self.mValue = None

    def createValue(self, data):
        # Tidy first
        self.mValue = None

        # Get value type from property name
        type = PyCalendarProperty.sDefaultValueTypeMap.get(self.mName.upper(), PyCalendarValue.VALUETYPE_TEXT)

        # Check whether custom value is set
        if self.mAttributes.has_key(definitions.cICalAttribute_VALUE):
            type = PyCalendarProperty.sValueTypeMap.get(self.getAttributeValue(definitions.cICalAttribute_VALUE), type)

        # Check for multivalued
        if self.mName.upper() in PyCalendarProperty.sMultiValues:
            self.mValue = PyCalendarMultiValue(type)
        else:
            # Create the type
            self.mValue = PyCalendarValue.createFromType(type)

        # Now parse the data
        try:
            self.mValue.parse(data)
        except ValueError:
            raise PyCalendarInvalidProperty("Invalid property value", data)

        # Special post-create for some types
        if type in (PyCalendarValue.VALUETYPE_TIME, PyCalendarValue.VALUETYPE_DATETIME):
            # Look for TZID attribute
            tzid = None
            if (self.hasAttribute(definitions.cICalAttribute_TZID)):
                tzid = self.getAttributeValue(definitions.cICalAttribute_TZID)
                
                if isinstance(self.mValue, PyCalendarDateTimeValue):
                    self.mValue.getValue().setTimezoneID(tzid)
                elif isinstance(self.mValue, PyCalendarMultiValue):
                    for item in self.mValue.getValues():
                        if isinstance(item, PyCalendarDateTimeValue):
                            item.getValue().setTimezoneID(tzid)

    def setValue(self, value):
        # Tidy first
        self.mValue = None

        # Get value type from property name
        type = PyCalendarProperty.sDefaultValueTypeMap.get(self.mName.upper(), PyCalendarValue.VALUETYPE_TEXT)

        # Check whether custom value is set
        if self.mAttributes.has_key(definitions.cICalAttribute_VALUE):
            type = PyCalendarProperty.sValueTypeMap.get(self.getAttributeValue(definitions.cICalAttribute_VALUE), type)

        # Check for multivalued
        if self.mName.upper() in PyCalendarProperty.sMultiValues:
            self.mValue = PyCalendarMultiValue(type)
        else:
            # Create the type
            self.mValue = PyCalendarValue.createFromType(type)

        self.mValue.setValue(value)

        # Special post-create for some types
        if type in (PyCalendarValue.VALUETYPE_TIME, PyCalendarValue.VALUETYPE_DATETIME):
            # Look for TZID attribute
            tzid = None
            if (self.hasAttribute(definitions.cICalAttribute_TZID)):
                tzid = self.getAttributeValue(definitions.cICalAttribute_TZID)
                
                if isinstance(self.mValue, PyCalendarDateTimeValue):
                    self.mValue.getValue().setTimezoneID(tzid)
                elif isinstance(self.mValue, PyCalendarMultiValue):
                    for item in self.mValue.getValues():
                        if isinstance(item, PyCalendarDateTimeValue):
                            item.getValue().setTimezoneID(tzid)

    def setupValueAttribute(self):
        if self.mAttributes.has_key(definitions.cICalAttribute_VALUE):
            del self.mAttributes[definitions.cICalAttribute_VALUE]

        # Only if we have a value right now
        if self.mValue is None:
            return

        # See if current type is default for this property
        default_type = self.sDefaultValueTypeMap.get(self.mName.upper())
        if default_type is not None:
            actual_type = self.mValue.getType()
            if default_type != actual_type:
                actual_value = self.sTypeValueMap.get(actual_type)
                if actual_value is not None:
                    self.mAttributes.setdefault(definitions.cICalAttribute_VALUE, []).append(PyCalendarAttribute(name=definitions.cICalAttribute_VALUE, value=actual_value))

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

    def _init_attr_value_requeststatus(self, reqstatus):
        # Value
        self.mValue = PyCalendarRequestStatusValue(reqstatus)

        # Attributes
        self.setupValueAttribute()

    def _init_attr_value_datetime(self, dt):
        # Value
        self.mValue = PyCalendarDateTimeValue(value=dt)

        # Attributes
        self.setupValueAttribute()

        # Look for timezone
        if not dt.isDateOnly() and dt.local():
            if self.mAttributes.has_key(definitions.cICalAttribute_TZID):
                del self.mAttributes[definitions.cICalAttribute_TZID]
            self.mAttributes.setdefault(definitions.cICalAttribute_TZID, []).append(
                    PyCalendarAttribute(name=definitions.cICalAttribute_TZID, value=dt.getTimezoneID()))
    
    def _init_attr_value_datetimelist(self, dtl):
        # Value
        date_only = (len(dtl) > 0) and dtl[0].isDateOnly()
        if date_only:
            self.mValue = PyCalendarMultiValue(PyCalendarValue.VALUETYPE_DATE)
        else:
            self.mValue = PyCalendarMultiValue(PyCalendarValue.VALUETYPE_DATETIME)

        for dt in dtl:
            self.mValue.addValue(PyCalendarDateTimeValue(dt))

        # Attributes
        self.setupValueAttribute()

        # Look for timezone
        if ((len(dtl) > 0)
                and not dtl[0].isDateOnly()
                and dtl[0].local()):
            if self.mAttributes.has_key(definitions.cICalAttribute_TZID):
                del self.mAttributes[definitions.cICalAttribute_TZID]
            self.mAttributes.setdefault(definitions.cICalAttribute_TZID, []).append(
                    PyCalendarAttribute(name=definitions.cICalAttribute_TZID, value=dtl[0].getTimezoneID()))

    def _init_attr_value_periodlist(self, periodlist):
        # Value
        self.mValue = PyCalendarMultiValue(PyCalendarValue.VALUETYPE_PERIOD)
        for period in periodlist:
            self.mValue.addValue(PyCalendarPeriodValue(period))

        # Attributes
        self.setupValueAttribute()

    def _init_attr_value_duration(self, du):
        # Value
        self.mValue = PyCalendarDurationValue(value=du)

        # Attributes
        self.setupValueAttribute()


    def _init_attr_value_period(self, pe):
        # Value
        self.mValue = PyCalendarPeriodValue(value=pe)

        # Attributes
        self.setupValueAttribute()


    def _init_attr_value_recur(self, recur):
        # Value
        self.mValue = PyCalendarRecurrenceValue(value=recur)

        # Attributes
        self.setupValueAttribute()

    def _init_attr_value_utcoffset(self, utcoffset):
        # Value
        self.mValue = PyCalendarUTCOffsetValue()
        self.mValue.setValue(utcoffset.getValue())

        # Attributes
        self.setupValueAttribute()
