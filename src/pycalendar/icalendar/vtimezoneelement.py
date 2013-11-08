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

from bisect import bisect_right
from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.recurrenceset import RecurrenceSet
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS
from pycalendar.period import Period
from pycalendar.value import Value

class VTimezoneElement(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTART,
        definitions.cICalProperty_TZOFFSETTO,
        definitions.cICalProperty_TZOFFSETFROM,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_RRULE,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None, dt=None, offset=None):
        super(VTimezoneElement, self).__init__(parent=parent)
        self.mStart = dt if dt is not None else DateTime()
        self.mTZName = ""
        self.mUTCOffset = offset if offset is not None else 0
        self.mUTCOffsetFrom = 0
        self.mRecurrences = RecurrenceSet()
        self.mCachedExpandBelow = None
        self.mCachedExpandBelowItems = None


    def duplicate(self, parent=None):
        other = super(VTimezoneElement, self).duplicate(parent=parent)
        other.mStart = self.mStart.duplicate()
        other.mTZName = self.mTZName
        other.mUTCOffset = self.mUTCOffset
        other.mUTCOffsetFrom = self.mUTCOffsetFrom
        other.mRecurrences = self.mRecurrences.duplicate()
        other.mCachedExpandBelow = None
        other.mCachedExpandBelowItems = None
        return other


    def finalise(self):
        # Get DTSTART
        temp = self.loadValueDateTime(definitions.cICalProperty_DTSTART)
        if temp is not None:
            self.mStart = temp

        # Get TZOFFSETTO
        temp = self.loadValueInteger(definitions.cICalProperty_TZOFFSETTO, Value.VALUETYPE_UTC_OFFSET)
        if temp is not None:
            self.mUTCOffset = temp

        # Get TZOFFSETFROM
        temp = self.loadValueInteger(definitions.cICalProperty_TZOFFSETFROM, Value.VALUETYPE_UTC_OFFSET)
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
        super(VTimezoneElement, self).finalise()


    def getSortKey(self):
        """
        We do not want these components sorted.
        """
        return ""


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

            temp = DateTime(below.getYear(), 1, 1, 0, 0, 0)

            # Use cache of expansion
            if self.mCachedExpandBelowItems is None:
                self.mCachedExpandBelowItems = []
            if self.mCachedExpandBelow is None:
                self.mCachedExpandBelow = self.mStart.duplicate()
            if temp > self.mCachedExpandBelow:
                self.mCachedExpandBelowItems = []
                period = Period(self.mStart, temp)
                self.mRecurrences.expand(self.mStart, period, self.mCachedExpandBelowItems, float_offset=self.mUTCOffsetFrom)
                self.mCachedExpandBelow = temp

            if len(self.mCachedExpandBelowItems) != 0:
                # List comes back sorted so we pick the element just less than
                # the dt value we want
                i = bisect_right(self.mCachedExpandBelowItems, below)
                if i != 0:
                    return self.mCachedExpandBelowItems[i - 1]

                # The first one in the list is the one we want
                return self.mCachedExpandBelowItems[0]

            return self.mStart


    def expandAll(self, start, end, with_name):

        if start is None:
            start = self.mStart

        # Ignore if there is no change in offset
        offsetto = self.loadValueInteger(definitions.cICalProperty_TZOFFSETTO, Value.VALUETYPE_UTC_OFFSET)
        offsetfrom = self.loadValueInteger(definitions.cICalProperty_TZOFFSETFROM, Value.VALUETYPE_UTC_OFFSET)
#        if offsetto == offsetfrom:
#            return ()

        # Look for recurrences
        if self.mStart > end:
            # Return nothing
            return ()
        elif not self.mRecurrences.hasRecurrence():
            # Return DTSTART even if it is newer
            if self.mStart >= start:
                result = (self.mStart, offsetfrom, offsetto,)
                if with_name:
                    result += (self.getTZName(),)
                return (result,)
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

            temp = DateTime(end.getYear(), 1, 1, 0, 0, 0)

            # Use cache of expansion
            if self.mCachedExpandBelowItems is None:
                self.mCachedExpandBelowItems = []
            if self.mCachedExpandBelow is None:
                self.mCachedExpandBelow = self.mStart.duplicate()
            if temp > self.mCachedExpandBelow:
                self.mCachedExpandBelowItems = []
                period = Period(self.mStart, end)
                self.mRecurrences.expand(self.mStart, period, self.mCachedExpandBelowItems, float_offset=self.mUTCOffsetFrom)
                self.mCachedExpandBelow = temp

            if len(self.mCachedExpandBelowItems) != 0:
                # Return them all within the range
                results = []
                for dt in self.mCachedExpandBelowItems:
                    if dt >= start and dt < end:
                        result = (dt, offsetfrom, offsetto,)
                        if with_name:
                            result += (self.getTZName(),)
                        results.append(result)
                return results

            return ()
