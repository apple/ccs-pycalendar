##
#    Copyright (c) 2007 Cyrus Daboo. All rights reserved.
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

from datetime import PyCalendarDateTime
from period import PyCalendarPeriod
from recurrenceset import PyCalendarRecurrenceSet
from value import PyCalendarValue
from vtimezone import PyCalendarVTimezone
import definitions

class PyCalendarVTimezoneElement(PyCalendarVTimezone):

    def __init__(self, calendar=None, dt=None, offset=None, copyit=None):
        if calendar is not None and dt is None:
            super(PyCalendarVTimezoneElement, self).__init__(calendar=calendar)
            self.mStart = PyCalendarDateTime()
            self.mTZName = ""
            self.mUTCOffset = 0
            self.mUTCOffsetFrom = 0
            self.mRecurrences = PyCalendarRecurrenceSet()
            self.mCachedExpandBelow = None
            self.mCachedExpandBelowItems = None
        elif calendar is not None and dt is not None:
            super(PyCalendarVTimezoneElement, self).__init__(calendar=calendar)
            self.mStart = dt
            self.mTZName = ""
            self.mUTCOffset = offset
            self.mUTCOffsetFrom = 0
            self.mRecurrences = PyCalendarRecurrenceSet()
            self.mCachedExpandBelow = None
            self.mCachedExpandBelowItems = None
        elif copyit:
            super(PyCalendarVTimezoneElement, self).__init__(copyit=copyit)
            self.mStart = PyCalendarDateTime(copyit=copyit.mStart)
            self.mTZName = copyit.mTZName
            self.mUTCOffset = copyit.mUTCOffset
            self.mUTCOffsetFrom = copyit.mUTCOffsetFrom
            self.mRecurrences = copyit.mRecurrences
            self.mCachedExpandBelow = None
            self.mCachedExpandBelowItems = None

    def finalise(self):
        # Get DTSTART
        temp = self.loadValueDateTime(definitions.cICalProperty_DTSTART)
        if temp is not None:
            self.mStart = temp

        # Get TZOFFSETTO
        temp = self.loadValueInteger(definitions.cICalProperty_TZOFFSETTO, PyCalendarValue.VALUETYPE_UTC_OFFSET)
        if temp is not None:
            self.mUTCOffset = temp

        # Get TZOFFSETFROM
        temp = self.loadValueInteger(definitions.cICalProperty_TZOFFSETFROM, PyCalendarValue.VALUETYPE_UTC_OFFSET)
        if temp is not None:
            self.mUTCOffsetFrom = temp

        # Get TZNAME
        temps = self.loadValueString(definitions.cICalProperty_TZNAME)
        if temps is not None:
            self.mTZName = temps

        # Get RRULEs
        self.loadValueRRULE(definitions.cICalProperty_RRULE, self.mRecurrences, True)

        # Get RDATEs
        self.loadValueRDATE(definitions.cICalProperty_RDATE, self.mRecurrences, True)

        # Do inherited
        super(PyCalendarVTimezoneElement, self).finalise()

    def getStart(self):
        return self.mStart

    def getUTCOffset(self):
        return self.mUTCOffset

    def getUTCOffsetFrom(self):
        return self.mUTCOffsetFrom

    def getTZName(self):
        return self.mTZName

    def expandBelow(self, below):
        
        # Look for recurrences
        if not self.mRecurrences.hasRecurrence() or self.mStart > below:
            # Return DTSTART even if it is newer
            return self.mStart
        else:
            # We want to allow recurrence calculation caching to help us here
            # as this method
            # gets called a lot - most likely for ever increasing dt values
            # (which will therefore
            # invalidate the recurrence cache).
            #
            # What we will do is round up the date-time to the next year so
            # that the recurrence
            # cache is invalidated less frequently

            temp = PyCalendarDateTime(copyit=below)
            temp.setMonth(1)
            temp.setDay(1)
            temp.setHHMMSS(0, 0, 0)
            temp.offsetYear(1)

            # Use cache of expansion
            if self.mCachedExpandBelowItems is None:
                self.mCachedExpandBelowItems = []
            if self.mCachedExpandBelow is None:
                self.mCachedExpandBelow = PyCalendarDateTime(copyit=self.mStart)
            if temp > self.mCachedExpandBelow:
                self.mCachedExpandBelowItems = []
                period = PyCalendarPeriod(self.mStart, temp)
                self.mRecurrences.expand(self.mStart, period, self.mCachedExpandBelowItems, float_offset=self.mUTCOffsetFrom)
                self.mCachedExpandBelow = temp
            
            if len(self.mCachedExpandBelowItems) != 0:
                # List comes back sorted so we pick the element just less than
                # the dt value we want
                for i in range(len(self.mCachedExpandBelowItems)):
                    if self.mCachedExpandBelowItems[i] > below:
                        if i != 0:
                            return self.mCachedExpandBelowItems[i - 1]
                        break
                
                # The last one in the list is the one we want
                return self.mCachedExpandBelowItems[len(self.mCachedExpandBelowItems) - 1]

            return self.mStart

    def expandAll(self, start, end):

        # Ignore if there is no change in offset
        offsetto = self.loadValueInteger(definitions.cICalProperty_TZOFFSETTO, PyCalendarValue.VALUETYPE_UTC_OFFSET)
        offsetfrom = self.loadValueInteger(definitions.cICalProperty_TZOFFSETFROM, PyCalendarValue.VALUETYPE_UTC_OFFSET)
#        if offsetto == offsetfrom:
#            return ()

        # Look for recurrences
        if self.mStart > end:
            # Return nothing
            return ()
        elif not self.mRecurrences.hasRecurrence():
            # Return DTSTART even if it is newer
            if self.mStart >= start:
                return ((self.mStart, offsetfrom, offsetto),)
            else:
                return ()
        else:
            # We want to allow recurrence calculation caching to help us here
            # as this method
            # gets called a lot - most likely for ever increasing dt values
            # (which will therefore
            # invalidate the recurrence cache).
            #
            # What we will do is round up the date-time to the next year so
            # that the recurrence
            # cache is invalidated less frequently

            temp = PyCalendarDateTime(copyit=end)
            temp.setMonth(1)
            temp.setDay(1)
            temp.setHHMMSS(0, 0, 0)
            temp.offsetYear(1)

            # Use cache of expansion
            if self.mCachedExpandBelowItems is None:
                self.mCachedExpandBelowItems = []
            if self.mCachedExpandBelow is None:
                self.mCachedExpandBelow = PyCalendarDateTime(copyit=self.mStart)
            if temp > self.mCachedExpandBelow:
                self.mCachedExpandBelowItems = []
                period = PyCalendarPeriod(start, end)
                self.mRecurrences.expand(self.mStart, period, self.mCachedExpandBelowItems, float_offset=self.mUTCOffsetFrom)
                self.mCachedExpandBelow = temp
            
            if len(self.mCachedExpandBelowItems) != 0:
                # The last one in the list is the one we want
                return [(dt, offsetfrom, offsetto,) for dt in self.mCachedExpandBelowItems]

            return ()
