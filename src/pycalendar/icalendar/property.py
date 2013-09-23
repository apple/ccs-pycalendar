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

from pycalendar.parameter import Parameter
from pycalendar.datetime import DateTime
from pycalendar.datetimevalue import DateTimeValue
from pycalendar.duration import Duration
from pycalendar.durationvalue import DurationValue
from pycalendar.icalendar import definitions
from pycalendar.icalendar.recurrence import Recurrence
from pycalendar.icalendar.recurrencevalue import RecurrenceValue
from pycalendar.icalendar.requeststatusvalue import RequestStatusValue
from pycalendar.multivalue import MultiValue
from pycalendar.period import Period
from pycalendar.periodvalue import PeriodValue
from pycalendar.property import PropertyBase
from pycalendar.utcoffsetvalue import UTCOffsetValue
from pycalendar.value import Value

class Property(PropertyBase):

    sDefaultValueTypeMap = {

        # 5545 Section 3.7
        definitions.cICalProperty_CALSCALE         : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_METHOD           : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_PRODID           : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_VERSION          : Value.VALUETYPE_TEXT,

        # 5545 Section 3.8.1
        definitions.cICalProperty_ATTACH           : Value.VALUETYPE_URI,
        definitions.cICalProperty_CATEGORIES       : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_CLASS            : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_COMMENT          : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_DESCRIPTION      : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_GEO              : Value.VALUETYPE_FLOAT,
        definitions.cICalProperty_LOCATION         : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_PERCENT_COMPLETE : Value.VALUETYPE_INTEGER,
        definitions.cICalProperty_PRIORITY         : Value.VALUETYPE_INTEGER,
        definitions.cICalProperty_RESOURCES        : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_STATUS           : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_SUMMARY          : Value.VALUETYPE_TEXT,

        # 5545 Section 3.8.2
        definitions.cICalProperty_COMPLETED : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_DTEND     : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_DUE       : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_DTSTART   : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_DURATION  : Value.VALUETYPE_DURATION,
        definitions.cICalProperty_FREEBUSY  : Value.VALUETYPE_PERIOD,
        definitions.cICalProperty_TRANSP    : Value.VALUETYPE_TEXT,

        # 5545 Section 3.8.3
        definitions.cICalProperty_TZID         : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_TZNAME       : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_TZOFFSETFROM : Value.VALUETYPE_UTC_OFFSET,
        definitions.cICalProperty_TZOFFSETTO   : Value.VALUETYPE_UTC_OFFSET,
        definitions.cICalProperty_TZURL        : Value.VALUETYPE_URI,

        # 5545 Section 3.8.4
        definitions.cICalProperty_ATTENDEE      : Value.VALUETYPE_CALADDRESS,
        definitions.cICalProperty_CONTACT       : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_ORGANIZER     : Value.VALUETYPE_CALADDRESS,
        definitions.cICalProperty_RECURRENCE_ID : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_RELATED_TO    : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_URL           : Value.VALUETYPE_URI,
        definitions.cICalProperty_UID           : Value.VALUETYPE_TEXT,

        # 5545 Section 3.8.5
        definitions.cICalProperty_EXDATE : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_EXRULE : Value.VALUETYPE_RECUR, # 2445 only
        definitions.cICalProperty_RDATE  : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_RRULE  : Value.VALUETYPE_RECUR,

        # 5545 Section 3.8.6
        definitions.cICalProperty_ACTION  : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_REPEAT  : Value.VALUETYPE_INTEGER,
        definitions.cICalProperty_TRIGGER : Value.VALUETYPE_DURATION,

        # 5545 Section 3.8.7
        definitions.cICalProperty_CREATED       : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_DTSTAMP       : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_LAST_MODIFIED : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_SEQUENCE      : Value.VALUETYPE_INTEGER,

        # 5545 Section 3.8.8
        definitions.cICalProperty_REQUEST_STATUS : Value.VALUETYPE_TEXT,

        # Extensions: draft-daboo-valarm-extensions-03
        definitions.cICalProperty_ACKNOWLEDGED   : Value.VALUETYPE_DATETIME,

        # Extensions: draft-york-vpoll-00.txt
        # Section 4.2
        definitions.cICalProperty_ACCEPT_RESPONSE   : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_POLL_ITEM_ID      : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_POLL_WINNER       : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_POLL_MODE         : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_POLL_PROPERTIES   : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_VOTER             : Value.VALUETYPE_CALADDRESS,

        # Apple Extensions
        definitions.cICalProperty_XWRCALNAME  : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_XWRCALDESC  : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_XWRALARMUID : Value.VALUETYPE_TEXT,

        # Mulberry extensions
        definitions.cICalProperty_ACTION_X_SPEAKTEXT  : Value.VALUETYPE_TEXT,
        definitions.cICalProperty_ALARM_X_LASTTRIGGER : Value.VALUETYPE_DATETIME,
        definitions.cICalProperty_ALARM_X_ALARMSTATUS : Value.VALUETYPE_TEXT,
    }

    sValueTypeMap = {

        # 5545 Section 3.3
        definitions.cICalValue_BINARY      : Value.VALUETYPE_BINARY,
        definitions.cICalValue_BOOLEAN     : Value.VALUETYPE_BOOLEAN,
        definitions.cICalValue_CAL_ADDRESS : Value.VALUETYPE_CALADDRESS,
        definitions.cICalValue_DATE        : Value.VALUETYPE_DATE,
        definitions.cICalValue_DATE_TIME   : Value.VALUETYPE_DATETIME,
        definitions.cICalValue_DURATION    : Value.VALUETYPE_DURATION,
        definitions.cICalValue_FLOAT       : Value.VALUETYPE_FLOAT,
        definitions.cICalValue_INTEGER     : Value.VALUETYPE_INTEGER,
        definitions.cICalValue_PERIOD      : Value.VALUETYPE_PERIOD,
        definitions.cICalValue_RECUR       : Value.VALUETYPE_RECUR,
        definitions.cICalValue_TEXT        : Value.VALUETYPE_TEXT,
        definitions.cICalValue_TIME        : Value.VALUETYPE_TIME,
        definitions.cICalValue_URI         : Value.VALUETYPE_URI,
        definitions.cICalValue_UTC_OFFSET  : Value.VALUETYPE_UTC_OFFSET,
    }

    sTypeValueMap = {

        # 5545 Section 3.3
        Value.VALUETYPE_BINARY         : definitions.cICalValue_BINARY,
        Value.VALUETYPE_BOOLEAN        : definitions.cICalValue_BOOLEAN,
        Value.VALUETYPE_CALADDRESS     : definitions.cICalValue_CAL_ADDRESS,
        Value.VALUETYPE_DATE           : definitions.cICalValue_DATE,
        Value.VALUETYPE_DATETIME       : definitions.cICalValue_DATE_TIME,
        Value.VALUETYPE_DURATION       : definitions.cICalValue_DURATION,
        Value.VALUETYPE_FLOAT          : definitions.cICalValue_FLOAT,
        Value.VALUETYPE_GEO            : definitions.cICalValue_FLOAT,
        Value.VALUETYPE_INTEGER        : definitions.cICalValue_INTEGER,
        Value.VALUETYPE_PERIOD         : definitions.cICalValue_PERIOD,
        Value.VALUETYPE_RECUR          : definitions.cICalValue_RECUR,
        Value.VALUETYPE_TEXT           : definitions.cICalValue_TEXT,
        Value.VALUETYPE_REQUEST_STATUS : definitions.cICalValue_TEXT,
        Value.VALUETYPE_TIME           : definitions.cICalValue_TIME,
        Value.VALUETYPE_URI            : definitions.cICalValue_URI,
        Value.VALUETYPE_UTC_OFFSET     : definitions.cICalValue_UTC_OFFSET,
    }

    sMultiValues = set((
        definitions.cICalProperty_CATEGORIES,
        definitions.cICalProperty_RESOURCES,
        definitions.cICalProperty_FREEBUSY,
        definitions.cICalProperty_EXDATE,
        definitions.cICalProperty_RDATE,
    ))

    sSpecialVariants = {
        definitions.cICalProperty_GEO : Value.VALUETYPE_GEO,
        definitions.cICalProperty_REQUEST_STATUS: Value.VALUETYPE_REQUEST_STATUS,
    }

    sVariant = "ical"

    sValue = definitions.cICalParameter_VALUE
    sText = definitions.cICalValue_TEXT

    def __init__(self, name=None, value=None, valuetype=None):

        super(Property, self).__init__(name, value, valuetype)

        # The None check speeds up .duplicate()
        if value is None:
            pass

        # Order these based on most likely occurrence to speed up this method
        elif isinstance(value, str):
            self._init_attr_value_text(value, valuetype if valuetype else self.sDefaultValueTypeMap.get(self.mName.upper(), Value.VALUETYPE_UNKNOWN))

        elif isinstance(value, DateTime):
            self._init_attr_value_datetime(value)

        elif isinstance(value, Duration):
            self._init_attr_value_duration(value)

        elif isinstance(value, Recurrence):
            self._init_attr_value_recur(value)

        elif isinstance(value, Period):
            self._init_attr_value_period(value)

        elif isinstance(value, int):
            self._init_attr_value_int(value)

        elif isinstance(value, list):
            if name.upper() == definitions.cICalProperty_REQUEST_STATUS:
                self._init_attr_value_requeststatus(value)
            else:
                period_list = False
                if len(value) != 0:
                    period_list = isinstance(value[0], Period)
                if period_list:
                    self._init_attr_value_periodlist(value)
                else:
                    self._init_attr_value_datetimelist(value)

        elif isinstance(value, UTCOffsetValue):
            self._init_attr_value_utcoffset(value)


    def duplicate(self):
        other = Property(self.mName)
        for attrname, attrs in self.mParameters.items():
            other.mParameters[attrname] = [i.duplicate() for i in attrs]
        other.mValue = self.mValue.duplicate()

        return other


    def __hash__(self):
        return hash((
            self.mName,
            tuple([tuple(self.mParameters[attrname]) for attrname in sorted(self.mParameters.keys())]),
            self.mValue,
        ))


    def __eq__(self, other):
        if not isinstance(other, Property):
            return False
        return self.mName == other.mName and self.mValue == other.mValue and self.mParameters == other.mParameters


    def getRecurrenceValue(self):

        if isinstance(self.mValue, RecurrenceValue):
            return self.mValue
        else:
            return None


    def _postCreateValue(self, value_type):
        """
        Do some extra work after creating a value in this property.

        @param value_type: the iCalendar VALUE type for this property
        @type value_type: C{str}
        """

        # Look for TZID parameter
        if value_type in (Value.VALUETYPE_TIME, Value.VALUETYPE_DATETIME) and self.hasParameter(definitions.cICalParameter_TZID):
            tzid = self.getParameterValue(definitions.cICalParameter_TZID)

            if isinstance(self.mValue, DateTimeValue):
                self.mValue.getValue().setTimezoneID(tzid)

            elif isinstance(self.mValue, MultiValue):
                for item in self.mValue.getValues():
                    if isinstance(item, DateTimeValue):
                        item.getValue().setTimezoneID(tzid)


    # Creation
    def _init_attr_value_requeststatus(self, reqstatus):
        # Value
        self.mValue = RequestStatusValue(reqstatus)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_datetime(self, dt):
        # Value
        self.mValue = DateTimeValue(value=dt)

        # Parameters
        self.setupValueParameter()

        # Look for timezone
        if not dt.isDateOnly() and dt.local():
            if definitions.cICalParameter_TZID in self.mParameters:
                del self.mParameters[definitions.cICalParameter_TZID]
            self.mParameters.setdefault(definitions.cICalParameter_TZID, []).append(
                    Parameter(name=definitions.cICalParameter_TZID, value=dt.getTimezoneID()))


    def _init_attr_value_datetimelist(self, dtl):
        # Value
        date_only = (len(dtl) > 0) and dtl[0].isDateOnly()
        if date_only:
            self.mValue = MultiValue(Value.VALUETYPE_DATE)
        else:
            self.mValue = MultiValue(Value.VALUETYPE_DATETIME)

        for dt in dtl:
            self.mValue.addValue(DateTimeValue(dt))

        # Parameters
        self.setupValueParameter()

        # Look for timezone
        if ((len(dtl) > 0)
                and not dtl[0].isDateOnly()
                and dtl[0].local()):
            if definitions.cICalParameter_TZID in self.mParameters:
                del self.mParameters[definitions.cICalParameter_TZID]
            self.mParameters.setdefault(definitions.cICalParameter_TZID, []).append(
                    Parameter(name=definitions.cICalParameter_TZID, value=dtl[0].getTimezoneID()))


    def _init_attr_value_periodlist(self, periodlist):
        # Value
        self.mValue = MultiValue(Value.VALUETYPE_PERIOD)
        for period in periodlist:
            self.mValue.addValue(PeriodValue(period))

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_duration(self, du):
        # Value
        self.mValue = DurationValue(value=du)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_period(self, pe):
        # Value
        self.mValue = PeriodValue(value=pe)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_recur(self, recur):
        # Value
        self.mValue = RecurrenceValue(value=recur)

        # Parameters
        self.setupValueParameter()
