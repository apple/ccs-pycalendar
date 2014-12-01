##
#    Copyright (c) 2014 Cyrus Daboo. All rights reserved.
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

from pycalendar.icalendar import definitions
from pycalendar.icalendar.icudatetime import ICUDateTime
import collections

class RecurrenceIterator(collections.Iterator):
    """
    An iterator that iterates a simple recurrence pattern.
    """

    def __init__(self, start, freq, interval, rscale=None, skip=definitions.eRecurrence_SKIP_YES, allow_invalid=False):
        """
        @param start: the start date-time
        @type start: L{DateTime} or L{ICUDateTime}
        @param freq: the frequency of iteration
        @type freq: L{int}
        @param interval: the interval for each iteration
        @type interval: L{int}
        @param rscale: calendar scale to apply recurrence pattern to
        @type rscale: L{str}
        @param skip: skipping behavior for invalid dates
        @type skip: L{int}
        @param allow_invalid: whether or not invalid values are allowed
        @type allow_invalid: L{InvalidDateTime}
        """
        self.start = start
        self.freq = freq
        self.interval = interval
        self.rscale = rscale
        self.skip = skip
        self.allow_invalid = allow_invalid

        self.step = 0

        # If an RSCALE is set, the C{self.start} value is a normal L{DateTime} object but we want
        # to have the recurrence apply to the non-Gregorian calendar. So convert the C{self.start}
        # value into the corresponding L{ICUDateTime} object.
        if self.rscale:
            self.start = ICUDateTime.fromDateTime(self.start, self.rscale)


    def __iter__(self):
        return self


    def next(self):
        """
        Iterate one step of the recurrence. Always return an L{DateTime} for an rscale based
        recurrence.

        @return: the resulting date-time - this object is not re-used by the iterator so can be used
            directly by the caller without any need to copy it
        @rtype L{DateTime}
        """

        dt = self.nextraw()

        # Always return the L{DateTime} equivalent when using C{self.rscale}
        return dt.toDateTime() if self.rscale else dt


    def nextraw(self):
        """
        Iterate one step of the recurrence using the native date-time calendar scale, and return
        the native value.

        @return: the resulting date-time - this object is not re-used by the iterator so can be used
            directly by the caller without any need to copy it
        @rtype L{DateTime} or L{ICUDateTime}
        """

        dt = self.start.duplicate()

        # Add appropriate interval
        if self.freq == definitions.eRecurrence_SECONDLY:
            dt.offsetSeconds(self.step)
        elif self.freq == definitions.eRecurrence_MINUTELY:
            dt.offsetMinutes(self.step)
        elif self.freq == definitions.eRecurrence_HOURLY:
            dt.offsetHours(self.step)
        elif self.freq == definitions.eRecurrence_DAILY:
            dt.offsetDay(self.step)
        elif self.freq == definitions.eRecurrence_WEEKLY:
            dt.offsetDay(7 * self.step)
        elif self.freq == definitions.eRecurrence_MONTHLY:
            dt.offsetMonth(self.step)

            # Check whether the day matches the start - if not we stepped
            # to an invalid date so apply skip behavior
            if dt.getDay() != self.start.getDay():
                if self.allow_invalid:
                    dt.setInvalid(dt.getYear(), dt.getMonth(), self.start.getDay(), dt.getLeapMonth())
                elif self.skip == definitions.eRecurrence_SKIP_YES:
                    # Iterate until we have a valid month
                    while dt.getDay() != self.start.getDay():
                        self.step += self.interval
                        dt = self.start.duplicate()
                        dt.offsetMonth(self.step)
                elif self.skip == definitions.eRecurrence_SKIP_BACKWARD:
                    # Both ICU and PyCalendar skip back by default
                    pass
                elif self.skip == definitions.eRecurrence_SKIP_FORWARD:
                    # Go one day forward
                    dt.offsetDay(1)

        elif self.freq == definitions.eRecurrence_YEARLY:
            dt.offsetYear(self.step)

            # Check whether the month/day matches the start - if not we stepped
            # to an invalid date so apply skip behavior
            if dt.getDay() != self.start.getDay() or dt.getMonth() != self.start.getMonth() or dt.getLeapMonth() != self.start.getLeapMonth():
                if self.allow_invalid:
                    dt.setInvalid(dt.getYear(), self.start.getMonth(), self.start.getDay(), self.start.getLeapMonth())
                elif self.skip == definitions.eRecurrence_SKIP_YES:
                    # Iterate until we have a valid date-time
                    while dt.getDay() != self.start.getDay() or dt.getMonth() != self.start.getMonth() or dt.getLeapMonth() != self.start.getLeapMonth():
                        self.step += self.interval
                        dt = self.start.duplicate()
                        dt.offsetYear(self.step)
                elif self.skip == definitions.eRecurrence_SKIP_BACKWARD:
                    # Both ICU and PyCalendar skip back by default
                    pass
                elif self.skip == definitions.eRecurrence_SKIP_FORWARD:
                    # Go one day forward
                    dt.offsetDay(1)

        self.step += self.interval

        return dt


if __name__ == '__main__':
    icudt = ICUDateTime.fromDateComponents("gregorian", 2014, 1, 31)
    iter = RecurrenceIterator(icudt, definitions.eRecurrence_MONTHLY, 1, definitions.eRecurrence_SKIP_BACKWARD)
    for i in range(12):
        print(iter.next().getText())
