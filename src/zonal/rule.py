##
#    Copyright (c) 2007-2012 Cyrus Daboo. All rights reserved.
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

from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions
from pycalendar.icalendar.property import Property
from pycalendar.icalendar.recurrence import Recurrence
from pycalendar.icalendar.vtimezonedaylight import Daylight
from pycalendar.icalendar.vtimezonestandard import Standard
from pycalendar.utcoffsetvalue import UTCOffsetValue
from pycalendar.utils import daysInMonth
import utils

"""
Class that maintains a TZ data Rule.
"""

__all__ = (
    "Rule",
    "RuleSet",
)

class RuleSet(object):
    """
    A set of tzdata rules tied to a specific Rule name
    """

    def __init__(self):
        self.name = ""
        self.rules = []


    def __str__(self):
        return self.generate()


    def __eq__(self, other):
        return other and (
            self.name == other.name and
            self.rules == other.rules
        )


    def __ne__(self, other):
        return not self.__eq__(other)


    def parse(self, lines):
        """
        Parse the set of Rule lines from tzdata.

        @param lines: the lines to parse.
        @type lines: C{str}
        """

        splitlines = lines.split("\n")
        for line in splitlines:
            splits = line.expandtabs(1).split(" ")
            name = splits[1]
            assert name, "Must have a zone name: '%s'" % (lines,)
            if not self.name:
                self.name = name
            assert self.name == name, "Different zone names %s and %s: %s" % (self.name, name,)
            rule = Rule()
            rule.parse(line)
            self.rules.append(rule)


    def generate(self):
        """
        Generate a Rule line.

        @return: a C{str} with the Rule.
        """
        items = [rule.generate() for rule in self.rules]
        return "\n".join(items)


    def expand(self, results, zoneinfo, maxYear):
        """
        Expand the set of rules into transition/offset pairs for the entire RuleSet
        starting at the beginning and going up to maxYear at most.

        @param results: list to append results to
        @type results: C{list}
        @param zoneinfo: the Zone in which this RuleSet is being used
        @type zoneinfo: L{ZoneRule}
        @param maxYear: the maximum year to expand out to
        @type maxYear: C{int}
        """
        for rule in self.rules:
            rule.expand(results, zoneinfo, maxYear)



class Rule(object):
    """
    A tzdata Rule
    """

    # Some useful mapping tables

    LASTDAY_NAME_TO_DAY = {
        "lastSun": DateTime.SUNDAY,
        "lastMon": DateTime.MONDAY,
        "lastTue": DateTime.TUESDAY,
        "lastWed": DateTime.WEDNESDAY,
        "lastThu": DateTime.THURSDAY,
        "lastFri": DateTime.FRIDAY,
        "lastSat": DateTime.SATURDAY,
    }

    DAY_NAME_TO_DAY = {
        "Sun": DateTime.SUNDAY,
        "Mon": DateTime.MONDAY,
        "Tue": DateTime.TUESDAY,
        "Wed": DateTime.WEDNESDAY,
        "Thu": DateTime.THURSDAY,
        "Fri": DateTime.FRIDAY,
        "Sat": DateTime.SATURDAY,
    }

    LASTDAY_NAME_TO_RDAY = {
        "lastSun": definitions.eRecurrence_WEEKDAY_SU,
        "lastMon": definitions.eRecurrence_WEEKDAY_MO,
        "lastTue": definitions.eRecurrence_WEEKDAY_TU,
        "lastWed": definitions.eRecurrence_WEEKDAY_WE,
        "lastThu": definitions.eRecurrence_WEEKDAY_TH,
        "lastFri": definitions.eRecurrence_WEEKDAY_FR,
        "lastSat": definitions.eRecurrence_WEEKDAY_SA,
    }

    DAY_NAME_TO_RDAY = {
        DateTime.SUNDAY: definitions.eRecurrence_WEEKDAY_SU,
        DateTime.MONDAY: definitions.eRecurrence_WEEKDAY_MO,
        DateTime.TUESDAY: definitions.eRecurrence_WEEKDAY_TU,
        DateTime.WEDNESDAY: definitions.eRecurrence_WEEKDAY_WE,
        DateTime.THURSDAY: definitions.eRecurrence_WEEKDAY_TH,
        DateTime.FRIDAY: definitions.eRecurrence_WEEKDAY_FR,
        DateTime.SATURDAY: definitions.eRecurrence_WEEKDAY_SA,
    }

    MONTH_NAME_TO_POS = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    MONTH_POS_TO_NAME = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


    def __init__(self):
        self.name = ""
        self.fromYear = ""
        self.toYear = ""
        self.type = "-"
        self.inMonth = 0
        self.onDay = ""
        self.atTime = 0
        self.saveTime = 0
        self.letter = ""


    def __str__(self):
        return self.generate()


    def __eq__(self, other):
        return other and (
            self.name == other.name and
            self.fromYear == other.fromYear and
            self.toYear == other.toYear and
            self.type == other.type and
            self.inMonth == other.inMonth and
            self.onDay == other.onDay and
            self.atTime == other.atTime and
            self.saveTime == other.saveTime and
            self.letter == other.letter
        )


    def __ne__(self, other):
        return not self.__eq__(other)


    def parse(self, line):
        """
        Parse the Rule line from tzdata.

        @param line: the line to parse.
        @type line: C{str}
        """

        # Simply split the bits up and store them in various properties
        splits = [x for x in line.expandtabs(1).split(" ") if len(x) > 0]
        assert len(splits) >= 10, "Wrong number of fields in Rule: '%s'" % (line,)
        self.name = splits[1]
        self.fromYear = splits[2]
        self.toYear = splits[3]
        self.type = splits[4]
        self.inMonth = splits[5]
        self.onDay = splits[6]
        self.atTime = splits[7]
        self.saveTime = splits[8]
        self.letter = splits[9]


    def generate(self):
        """
        Generate a Rule line.

        @return: a C{str} with the Rule.
        """
        items = (
            "Rule",
            self.name,
            self.fromYear,
            self.toYear,
            self.type,
            self.inMonth,
            self.onDay,
            self.atTime,
            self.saveTime,
            self.letter,
        )

        return "\t".join(items)


    def getOffset(self):
        """
        Return the specified rule offset in seconds.

        @return: C{int}
        """
        splits = self.saveTime.split(":")
        hours = int(splits[0])
        if len(splits) == 2:
            minutes = int(splits[1])
        else:
            minutes = 0
        negative = hours < 0
        if negative:
            return -((-hours * 60) + minutes) * 60
        else:
            return ((hours * 60) + minutes) * 60


    def startYear(self):
        return int(self.fromYear)


    def endYear(self):
        if self.toYear == "only":
            return self.startYear()
        elif self.toYear == "max":
            return 9999
        else:
            return int(self.toYear)


    def datetimeForYear(self, year):
        """
        Given a specific year, determine the actual date/time of the transition

        @param year:  the year to determine the transition for
        @type year: C{int}

        @return: C{tuple} of L{DateTime} and C{str} (which is the special
            tzdata mode character
        """
        # Create a floating date-time
        dt = DateTime()

        # Setup base year/month/day
        dt.setYear(year)
        dt.setMonth(Rule.MONTH_NAME_TO_POS[self.inMonth])
        dt.setDay(1)

        # Setup base hours/minutes
        splits = self.atTime.split(":")
        if len(splits) == 1:
            splits.append("0")
        assert len(splits) == 2, "atTime format is wrong: %s, %s" % (self.atTime, self,)
        hours = int(splits[0])
        if len(splits[1]) > 2:
            minutes = int(splits[1][:2])
            special = splits[1][2:]
        else:
            minutes = int(splits[1])
            special = ""

        # Special case for 24:00
        if hours == 24 and minutes == 0:
            dt.setHours(23)
            dt.setMinutes(59)
            dt.setSeconds(59)
        else:
            dt.setHours(hours)
            dt.setMinutes(minutes)

        # Now determine the actual start day
        if self.onDay in Rule.LASTDAY_NAME_TO_DAY:
            dt.setDayOfWeekInMonth(-1, Rule.LASTDAY_NAME_TO_DAY[self.onDay])
        elif self.onDay.find(">=") != -1:
            splits = self.onDay.split(">=")
            dt.setNextDayOfWeek(int(splits[1]), Rule.DAY_NAME_TO_DAY[splits[0]])
        else:
            try:
                day = int(self.onDay)
                dt.setDay(day)
            except:
                assert False, "onDay value is not recognized: %s" % (self.onDay,)

        return dt, special


    def getOnDayDetails(self, start, indicatedDay, indicatedOffset):
        """
        Get RRULE BYxxx part items from the Rule data.

        @param start: start date-time for the recurrence set
        @type start: L{DateTime}
        @param indicatedDay: the day that the Rule indicates for recurrence
        @type indicatedDay: C{int}
        @param indicatedOffset: the offset that the Rule indicates for recurrence
        @type indicatedOffset: C{int}
        """

        month = start.getMonth()
        year = start.getYear()
        dayOfWeek = start.getDayOfWeek()

        # Need to check whether day has changed due to time shifting
        # e.g. if "u" mode is specified, the actual localtime may be
        # shifted to the previous day if the offset is negative
        if indicatedDay != dayOfWeek:
            difference = dayOfWeek - indicatedDay
            if difference in (1, -6,):
                indicatedOffset += 1

                # Adjust the month down too if needed
                if start.getDay() == 1:
                    month -= 1
                    if month < 1:
                        month = 12
            elif difference in (-1, 6,):
                assert indicatedOffset != 1, "Bad RRULE adjustment"
                indicatedOffset -= 1
            else:
                assert False, "Unknown RRULE adjustment"

        try:
            # Form the appropriate RRULE bits
            day = Rule.DAY_NAME_TO_RDAY[dayOfWeek]
            offset = indicatedOffset
            bymday = None
            if offset == 1:
                offset = 1
            elif offset == 8:
                offset = 2
            elif offset == 15:
                offset = 3
            elif offset == 22:
                offset = 4
            else:
                days_in_month = daysInMonth(month, year)
                if days_in_month - offset == 6:
                    offset = -1
                elif days_in_month - offset == 13:
                    offset = -2
                elif days_in_month - offset == 20:
                    offset = -3
                else:
                    bymday = [offset + i for i in range(7) if (offset + i) <= days_in_month]
                    offset = 0
        except:
            assert False, "onDay value is not recognized: %s" % (self.onDay,)

        return offset, day, bymday


    def expand(self, results, zoneinfo, maxYear):
        """
        Expand the Rule into a set of transition date/offset pairs

        @param results: list to append results to
        @type results: C{list}
        @param zoneinfo: the Zone in which this RuleSet is being used
        @type zoneinfo: L{ZoneRule}
        @param maxYear: the maximum year to expand out to
        @type maxYear: C{int}
        """

        if self.startYear() >= maxYear:
            return

        self.fullExpand(maxYear)
        zoneoffset = zoneinfo.getUTCOffset()
        offset = self.getOffset()
        for dt in self.dt_cache:
            results.append((dt, zoneoffset + offset, self))


    def fullExpand(self, maxYear):
        """
        Do a full recurrence expansion for each year in the Rule's range, upto
        a specified maximum.

        @param maxYear: maximum year to expand to
        @type maxYear: C{int}
        """
        if hasattr(self, "dt_cache"):
            return self.dt_cache
        start = self.startYear()
        end = self.endYear()
        if end > maxYear:
            end = maxYear - 1
        self.dt_cache = []
        for year in xrange(start, end + 1):
            dt = utils.DateTime(*self.datetimeForYear(year))
            self.dt_cache.append(dt)


    def vtimezone(self, vtz, zonerule, start, end, offsetfrom, offsetto, instanceCount):
        """
        Generate a VTIMEZONE sub-component for this Rule.

        @param vtz: VTIMEZONE to add to
        @type vtz: L{VTimezone}
        @param zonerule: the Zone rule line being used
        @type zonerule: L{ZoneRule}
        @param start: the start time for the first instance
        @type start: L{DateTime}
        @param end: the start time for the last instance
        @type end: L{DateTime}
        @param offsetfrom: the UTC offset-from
        @type offsetfrom: C{int}
        @param offsetto: the UTC offset-to
        @type offsetto: C{int}
        @param instanceCount: the number of instances in the set
        @type instanceCount: C{int}
        """

        # Determine type of component based on offset
        dstoffset = self.getOffset()
        if dstoffset == 0:
            comp = Standard(parent=vtz)
        else:
            comp = Daylight(parent=vtz)

        # Do offsets
        tzoffsetfrom = UTCOffsetValue(offsetfrom)
        tzoffsetto = UTCOffsetValue(offsetto)

        comp.addProperty(Property(definitions.cICalProperty_TZOFFSETFROM, tzoffsetfrom))
        comp.addProperty(Property(definitions.cICalProperty_TZOFFSETTO, tzoffsetto))

        # Do TZNAME
        if zonerule.format.find("%") != -1:
            tzname = zonerule.format % (self.letter if self.letter != "-" else "",)
        else:
            tzname = zonerule.format
        comp.addProperty(Property(definitions.cICalProperty_TZNAME, tzname))

        # Do DTSTART
        comp.addProperty(Property(definitions.cICalProperty_DTSTART, start))

        # Now determine the recurrences (use RDATE if only one year or
        # number of instances is one)
        if self.toYear != "only" and instanceCount != 1:
            rrule = Recurrence()
            rrule.setFreq(definitions.eRecurrence_YEARLY)
            rrule.setByMonth((Rule.MONTH_NAME_TO_POS[self.inMonth],))
            if self.onDay in Rule.LASTDAY_NAME_TO_RDAY:

                # Need to check whether day has changed due to time shifting
                dayOfWeek = start.getDayOfWeek()
                indicatedDay = Rule.LASTDAY_NAME_TO_DAY[self.onDay]

                if dayOfWeek == indicatedDay:
                    rrule.setByDay(((-1, Rule.LASTDAY_NAME_TO_RDAY[self.onDay]),))
                elif dayOfWeek < indicatedDay or dayOfWeek == 6 and indicatedDay == 0:
                    # This is OK as we have moved back a day and thus no month transition
                    # could have occurred
                    fakeOffset = daysInMonth(start.getMonth(), start.getYear()) - 6
                    offset, rday, bymday = self.getOnDayDetails(start, indicatedDay, fakeOffset)
                    if bymday:
                        rrule.setByMonthDay(bymday)
                    rrule.setByDay(((offset, rday),))
                else:
                    # This is bad news as we have moved forward a day possibly into the next month
                    # What we do is switch to using a BYYEARDAY rule with offset from the end of the year
                    rrule.setByMonth(())
                    daysBackStartOfMonth = (
                        365, 334, 306, 275, 245, 214, 184, 153, 122, 92, 61, 31, 0     # Does not account for leap year
                    )
                    rrule.setByYearDay([-(daysBackStartOfMonth[Rule.MONTH_NAME_TO_POS[self.inMonth]] + i) for i in range(7)])
                    rrule.setByDay(
                        ((0, divmod(Rule.LASTDAY_NAME_TO_DAY[self.onDay] + 1, 7)[1]),),
                    )

            elif self.onDay.find(">=") != -1:
                indicatedDay, dayoffset = self.onDay.split(">=")

                # Need to check whether day has changed due to time shifting
                dayOfWeek = start.getDayOfWeek()
                indicatedDay = Rule.DAY_NAME_TO_DAY[indicatedDay]

                if dayOfWeek == indicatedDay:
                    offset, rday, bymday = self.getOnDayDetails(start, indicatedDay, int(dayoffset))
                    if bymday:
                        rrule.setByMonthDay(bymday)
                    rrule.setByDay(((offset, rday),))
                elif dayoffset == 1 and divmod(dayoffset - indicatedDay, 7)[1] == 6:
                    # This is bad news as we have moved backward a day possibly into the next month
                    # What we do is switch to using a BYYEARDAY rule with offset from the end of the year
                    rrule.setByMonth(())
                    daysBackStartOfMonth = (
                        365, 334, 306, 275, 245, 214, 184, 153, 122, 92, 61, 31, 0     # Does not account for leap year
                    )
                    rrule.setByYearDay([-(daysBackStartOfMonth[Rule.MONTH_NAME_TO_POS[self.inMonth]] + i) for i in range(7)])
                    rrule.setByDay(
                        ((0, divmod(indicatedDay + 1, 7)[1]),),
                    )
                else:
                    # This is OK as we have moved forward a day and thus no month transition
                    # could have occurred
                    offset, rday, bymday = self.getOnDayDetails(start, indicatedDay, int(dayoffset))
                    if bymday:
                        rrule.setByMonthDay(bymday)
                    rrule.setByDay(((offset, rday),))
            else:
                try:
                    _ignore_day = int(self.onDay)
                except:
                    assert False, "onDay value is not recognized: %s" % (self.onDay,)

            # Add any UNTIL
            if zonerule.getUntilDate().dt.getYear() < 9999 or self.endYear() < 9999:
                until = end.duplicate()
                until.offsetSeconds(-offsetfrom)
                until.setTimezoneUTC(True)
                rrule.setUseUntil(True)
                rrule.setUntil(until)

            comp.addProperty(Property(definitions.cICalProperty_RRULE, rrule))
        else:
            comp.addProperty(Property(definitions.cICalProperty_RDATE, start))

        comp.finalise()
        vtz.addComponent(comp)
