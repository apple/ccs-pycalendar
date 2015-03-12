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

from pycalendar import locale, xmldefinitions, xmlutils
from pycalendar import utils
from pycalendar.duration import Duration
from pycalendar.icalendar import definitions
from pycalendar.parser import ParserContext
from pycalendar.timezone import Timezone
from pycalendar.valueutils import ValueMixin
import cStringIO as StringIO
import time
import xml.etree.cElementTree as XML

class DateTime(ValueMixin):

    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

    FULLDATE = 0
    ABBREVDATE = 1
    NUMERICDATE = 2
    FULLDATENOYEAR = 3
    ABBREVDATENOYEAR = 4
    NUMERICDATENOYEAR = 5

    @staticmethod
    def sort(e1, e2):

        return e1.compareDateTime(e2)


    def __init__(self, year=None, month=None, day=None, hours=None, minutes=None, seconds=None, tzid=None, utcoffset=None):

        self.mYear = 1970
        self.mMonth = 1
        self.mDay = 1

        self.mHours = 0
        self.mMinutes = 0
        self.mSeconds = 0

        self.mDateOnly = False

        self.mTZUTC = False
        self.mTZID = None
        self.mTZOffset = None

        self.mPosixTimeCached = False
        self.mPosixTime = 0

        if (year is not None) and (month is not None) and (day is not None):
            self.mYear = year
            self.mMonth = month
            self.mDay = day
            if (hours is not None) and (minutes is not None) and (seconds is not None):
                self.mHours = hours
                self.mMinutes = minutes
                self.mSeconds = seconds
            else:
                self.mDateOnly = True
            if tzid:
                self.mTZUTC = tzid.getUTC()
                self.mTZID = tzid.getTimezoneID()


    def duplicate(self):
        other = DateTime(self.mYear, self.mMonth, self.mDay, self.mHours, self.mMinutes, self.mSeconds)

        other.mDateOnly = self.mDateOnly

        other.mTZUTC = self.mTZUTC
        other.mTZID = self.mTZID
        other.mTZOffset = self.mTZOffset

        other.mPosixTimeCached = self.mPosixTimeCached
        other.mPosixTime = self.mPosixTime

        return other


    def duplicateAsUTC(self):
        other = self.duplicate()
        other.adjustToUTC()
        return other


    def __repr__(self):
        return "DateTime: %s" % (self.getText(),)


    def __hash__(self):
        return hash(self.getPosixTime())


    # Operators
    def __add__(self, duration):
        # Add duration seconds to temp object and normalise it
        result = self.duplicate()
        result.mSeconds += duration.getTotalSeconds()
        result.normalise()
        return result


    def __sub__(self, dateorduration):

        if isinstance(dateorduration, DateTime):

            date = dateorduration

            # Look for floating
            if self.floating() or date.floating():
                # Adjust the floating ones to fixed
                copy1 = self.duplicate()
                copy2 = date.duplicate()

                if copy1.floating() and copy2.floating():
                    # Set both to UTC and do comparison
                    copy1.setTimezoneUTC(True)
                    copy2.setTimezoneUTC(True)
                    return copy1 - copy2
                elif copy1.floating():
                    # Set to be the same
                    copy1.setTimezoneID(copy2.getTimezoneID())
                    copy1.setTimezoneUTC(copy2.getTimezoneUTC())
                    return copy1 - copy2
                else:
                    # Set to be the same
                    copy2.setTimezoneID(copy1.getTimezoneID())
                    copy2.setTimezoneUTC(copy1.getTimezoneUTC())
                    return copy1 - copy2

            else:
                # Do diff of date-time in seconds
                diff = self.getPosixTime() - date.getPosixTime()
                return Duration(duration=diff)

        elif isinstance(dateorduration, Duration):

            duration = dateorduration
            result = self.duplicate()
            result.mSeconds -= duration.getTotalSeconds()
            result.normalise()
            return result

        raise ValueError


    # Comparators
    def __eq__(self, comp):
        return self.compareDateTime(comp) == 0


    def __ne__(self, comp):
        return self.compareDateTime(comp) != 0


    def __ge__(self, comp):
        return self.compareDateTime(comp) >= 0


    def __le__(self, comp):
        return self.compareDateTime(comp) <= 0


    def __gt__(self, comp):
        return self.compareDateTime(comp) > 0


    def __lt__(self, comp):
        return self.compareDateTime(comp) < 0


    def compareDateTime(self, comp):
        if comp is None:
            return 1
        # If either are date only, then just do date compare
        if self.mDateOnly or comp.mDateOnly:
            if self.mYear == comp.mYear:
                if self.mMonth == comp.mMonth:
                    if self.mDay == comp.mDay:
                        return 0
                    else:
                        if self.mDay < comp.mDay:
                            return -1
                        else:
                            return 1
                else:
                    if self.mMonth < comp.mMonth:
                        return -1
                    else:
                        return 1
            else:
                if self.mYear < comp.mYear:
                    return -1
                else:
                    return 1

        # If they have the same timezone do simple compare - no posix calc
        # needed
        elif (Timezone.same(self.mTZUTC, self.mTZID, comp.mTZUTC, comp.mTZID)):
            if self.mYear == comp.mYear:
                if self.mMonth == comp.mMonth:
                    if self.mDay == comp.mDay:
                        if self.mHours == comp.mHours:
                            if self.mMinutes == comp.mMinutes:
                                if self.mSeconds == comp.mSeconds:
                                    return 0
                                else:
                                    if self.mSeconds < comp.mSeconds:
                                        return -1
                                    else:
                                        return 1
                            else:
                                if self.mMinutes < comp.mMinutes:
                                    return -1
                                else:
                                    return 1
                        else:
                            if self.mHours < comp.mHours:
                                return -1
                            else:
                                return 1
                    else:
                        if self.mDay < comp.mDay:
                            return -1
                        else:
                            return 1
                else:
                    if self.mMonth < comp.mMonth:
                        return -1
                    else:
                        return 1
            else:
                if self.mYear < comp.mYear:
                    return -1
                else:
                    return 1
        else:
            posix1 = self.getPosixTime()
            posix2 = comp.getPosixTime()
            if posix1 == posix2:
                return 0
            else:
                if posix1 < posix2:
                    return -1
                else:
                    return 1


    def compareDate(self, comp):
        return (self.mYear == comp.mYear) and (self.mMonth == comp.mMonth) and (self.mDay == comp.mDay)


    def getPosixTime(self):
        # Look for cached value (or floating time which has to be calculated
        # each time)
        if (not self.mPosixTimeCached) or self.floating():
            result = 0L

            # Add hour/mins/secs
            result = (self.mHours * 60L + self.mMinutes) * 60L + self.mSeconds

            # Number of days since 1970
            result += self.daysSince1970() * 24L * 60L * 60L

            # Adjust for timezone offset
            result -= self.timeZoneSecondsOffset()

            # Now indicate cache state
            self.mPosixTimeCached = True
            self.mPosixTime = result

        return self.mPosixTime


    def isDateOnly(self):
        return self.mDateOnly


    def setDateOnly(self, date_only):
        self.mDateOnly = date_only
        self.changed()


    def setYYMMDD(self, year, month, days):
        if (self.mYear != year) or (self.mMonth != month) or (self.mDay != days):
            self.mYear = year
            self.mMonth = month
            self.mDay = days
            self.changed()


    def getYear(self):
        return self.mYear


    def setYear(self, year):
        if self.mYear != year:
            self.mYear = year
            self.changed()


    def offsetYear(self, diff_year):
        self.mYear += diff_year
        self.normalise()


    def getMonth(self):
        return self.mMonth


    def setMonth(self, month):
        if self.mMonth != month:
            self.mMonth = month
            self.changed()


    def offsetMonth(self, diff_month):
        self.mMonth += diff_month
        self.normalise()


    def getDay(self):
        return self.mDay


    def setDay(self, day):
        if self.mDay != day:
            self.mDay = day
            self.changed()


    def offsetDay(self, diff_day):
        self.mDay += diff_day
        self.normalise()


    def setYearDay(self, day, allow_invalid=False):
        # 1 .. 366 offset from start, or
        # -1 .. -366 offset from end

        if day == 366:
            self.mMonth = 12
            self.mDay = 31 if utils.isLeapYear(self.mYear) else 32

        elif day == -366:
            self.mMonth = 1 if utils.isLeapYear(self.mYear) else 1
            self.mDay = 1 if utils.isLeapYear(self.mYear) else 0

        elif day > 0:
            # Offset current date to 1st January of current year
            self.mMonth = 1
            self.mDay = 1

            # Increment day
            self.mDay += day - 1

        elif day < 0:
            # Offset current date to 1st January of next year
            self.mMonth = 12
            self.mDay = 31

            # Decrement day
            self.mDay += day + 1

        if not allow_invalid:
            # Normalise to get proper year/month/day values
            self.normalise()
        else:
            self.changed()


    def getYearDay(self):
        return self.mDay + utils.daysUptoMonth(self.mMonth, self.mYear)


    def setMonthDay(self, day, allow_invalid=False):
        # 1 .. 31 offset from start, or
        # -1 .. -31 offset from end

        if day > 0:
            # Offset current date to 1st of current month
            self.mDay = 1

            # Increment day
            self.mDay += day - 1

        elif day < 0:
            # Offset current date to last of month
            self.mDay = utils.daysInMonth(self.mMonth, self.mYear)

            # Decrement day
            self.mDay += day + 1

        if not allow_invalid:
            # Normalise to get proper year/month/day values
            self.normalise()
        else:
            self.changed()


    def isMonthDay(self, day):
        if day > 0:
            return self.mDay == day
        elif day < 0:
            return self.mDay - 1 - utils.daysInMonth(self.mMonth, self.mYear) == day
        else:
            return False


    def setWeekNo(self, weekno):
        """
        Set the current date to one with the same day of the week in the current year with the
        specified week number. Note this might cause the year to shift backwards or forwards
        if the date is at the boundary between two years.

        @param weekno: the week number to set (currently must be positive)
        @type weekno: C{int}
        """

        # Don't both if already correct
        if self.getWeekNo() == weekno:
            return

        # What day does the current year start on, and diff that with the current day
        temp = DateTime(year=self.mYear, month=1, day=1)
        first_day = temp.getDayOfWeek()
        current_day = self.getDayOfWeek()

        # Calculate and set yearday for start of week. The first week is the one that contains at least
        # four days (with week start defaulting to MONDAY), so that means the 1st of January would fall
        # on MO, TU, WE, TH.
        if first_day in (DateTime.MONDAY, DateTime.TUESDAY, DateTime.WEDNESDAY, DateTime.THURSDAY):
            year_day = (weekno - 1) * 7 + current_day - first_day
        else:
            year_day = weekno * 7 + current_day - first_day

        # It is possible we have a negative offset which means go back to the prior year as part of
        # week #1 exists at the end of that year.
        if year_day < 0:
            self.offsetYear(-1)
        else:
            year_day += 1
        self.setYearDay(year_day)


    def getWeekNo(self):
        """
        Return the ISO week number for the current date.
        """

        # What day does the current year start on
        temp = DateTime(year=self.mYear, month=1, day=1)
        first_day = temp.getDayOfWeek()
        if first_day == 0:
            first_day = 7
        current_day = self.getDayOfWeek()
        if current_day == 0:
            current_day = 7

        # This arithmetic uses the ISO day of week (1-7) and the year day to get the week number
        week_no = (self.getYearDay() - current_day + 10) / 7

        # Might need to adjust forward/backwards based on year boundaries
        if week_no == 0:
            # Last week of previous year
            temp = DateTime(year=self.mYear - 1, month=12, day=31)
            week_no = temp.getWeekNo()
        elif week_no == 53:
            # Might be first week of next year
            temp = DateTime(year=self.mYear + 1, month=1, day=1)
            first_day = temp.getDayOfWeek()
            if first_day in (DateTime.MONDAY, DateTime.TUESDAY, DateTime.WEDNESDAY, DateTime.THURSDAY):
                week_no = 1

        return week_no


    def isWeekNo(self, weekno):
        # This is the iso 8601 week number definition

        if weekno > 0:
            return self.getWeekNo() == weekno
        else:
            # This needs to calculate the negative offset from the last week in
            # the current year
            return False


    def setDayOfWeekInYear(self, offset, day):
        # Set to first day in year
        self.mMonth = 1
        self.mDay = 1

        # Determine first weekday in year
        first_day = self.getDayOfWeek()

        if offset > 0:
            cycle = (offset - 1) * 7 + day
            cycle -= first_day
            if first_day > day:
                cycle += 7
            self.mDay = cycle + 1
        elif offset < 0:
            first_day += 365 + [1, 0][not utils.isLeapYear(self.mYear)] - 1
            first_day %= 7

            cycle = (-offset - 1) * 7 - day
            cycle += first_day
            if day > first_day:
                cycle += 7
            self.mDay = 365 + [1, 0][not utils.isLeapYear(self.mYear)] - cycle

        self.normalise()


    def setDayOfWeekInMonth(self, offset, day, allow_invalid=False):
        # Set to first day in month
        self.mDay = 1

        # Determine first weekday in month
        first_day = self.getDayOfWeek()

        if offset > 0:
            cycle = (offset - 1) * 7 + day
            cycle -= first_day
            if first_day > day:
                cycle += 7
            self.mDay = cycle + 1
        elif offset < 0:
            days_in_month = utils.daysInMonth(self.mMonth, self.mYear)
            first_day += days_in_month - 1
            first_day %= 7

            cycle = (-offset - 1) * 7 - day
            cycle += first_day
            if day > first_day:
                cycle += 7
            self.mDay = days_in_month - cycle

        if not allow_invalid:
            self.normalise()
        else:
            self.changed()


    def setNextDayOfWeek(self, start, day):
        # Set to first day in month
        self.mDay = start

        # Determine first weekday in month
        first_day = self.getDayOfWeek()

        if first_day > day:
            self.mDay += 7

        self.mDay += day - first_day

        self.normalise()


    def isDayOfWeekInMonth(self, offset, day):
        # First of the actual day must match
        if self.getDayOfWeek() != day:
            return False

        # If there is no count the we match any of this day in the month
        if offset == 0:
            return True

        # Create temp date-time with the appropriate parameters and then
        # compare
        temp = self.duplicate()
        temp.setDayOfWeekInMonth(offset, day)

        # Now compare dates
        return self.compareDate(temp)


    def getDayOfWeek(self):
        # Count days since 01-Jan-1970 which was a Thursday
        result = DateTime.THURSDAY + self.daysSince1970()
        result %= 7
        if result < 0:
            result += 7

        return result


    def getMonthText(self, short_txt):
        # Make sure range is valid
        if (self.mMonth < 1) or (self.mMonth > 12):
            return ""
        else:
            return locale.getMonth(
                self.mMonth,
                [locale.SHORT, locale.LONG][not short_txt]
            )


    def getDayOfWeekText(self, day):
        return locale.getDay(day, locale.SHORT)


    def setHHMMSS(self, hours, minutes, seconds):
        if (self.mHours != hours) or (self.mMinutes != minutes) or (self.mSeconds != seconds):
            self.mHours = hours
            self.mMinutes = minutes
            self.mSeconds = seconds
            self.changed()


    def getHours(self):
        return self.mHours


    def setHours(self, hours):
        if self.mHours != hours:
            self.mHours = hours
            self.changed()


    def offsetHours(self, diff_hour):
        self.mHours += diff_hour
        self.normalise()


    def getMinutes(self):
        return self.mMinutes


    def setMinutes(self, minutes):
        if self.mMinutes != minutes:
            self.mMinutes = minutes
            self.changed()


    def offsetMinutes(self, diff_minutes):
        self.mMinutes += diff_minutes
        self.normalise()


    def getSeconds(self):
        return self.mSeconds


    def setSeconds(self, seconds):
        if self.mSeconds != seconds:
            self.mSeconds = seconds
            self.changed()


    def offsetSeconds(self, diff_seconds):
        self.mSeconds += diff_seconds
        self.normalise()


    def getTimezoneUTC(self):
        return self.mTZUTC


    def setTimezoneUTC(self, utc):
        if self.mTZUTC != utc:
            self.mTZUTC = utc
            self.changed()


    def getTimezoneID(self):
        return self.mTZID


    def setTimezoneID(self, tzid):
        self.mTZUTC = False
        self.mTZID = tzid
        self.changed()


    def utc(self):
        return self.mTZUTC


    def local(self):
        return (not self.mTZUTC) and self.mTZID


    def floating(self):
        return (not self.mTZUTC) and not self.mTZID


    def getTimezone(self):
        return Timezone(utc=self.mTZUTC, tzid=self.mTZID)


    def setTimezone(self, tzid):
        self.mTZUTC = tzid.getUTC()
        self.mTZID = tzid.getTimezoneID()
        self.changed()


    def adjustTimezone(self, tzid):
        # Only if different
        s1 = tzid.getTimezoneID()
        if (tzid.getUTC() != self.mTZUTC) or (s1 != self.mTZID):
            if not self.mTZUTC:
                self.adjustToUTC()
            self.setTimezone(tzid)
            offset_to = self.timeZoneSecondsOffset(relative_to_utc=True)
            self.offsetSeconds(offset_to)
        return self


    def adjustToUTC(self):
        if self.local() and not self.mDateOnly:
            # Cache and restore and adjust the posix value to avoid a recalc since it won't change during this adjust
            tempPosix = self.mPosixTime if self.mPosixTimeCached else None

            utc = Timezone(utc=True)

            offset_from = self.timeZoneSecondsOffset()
            self.setTimezone(utc)

            self.offsetSeconds(-offset_from)

            if tempPosix is not None:
                self.mPosixTimeCached = True
                self.mPosixTime = tempPosix

            self.mTZOffset = 0

        return self


    def getAdjustedTime(self, tzid=None):
        # Copy this and adjust to input timezone
        adjusted = self.duplicate()
        adjusted.adjustTimezone(tzid)
        return adjusted


    def setToday(self):
        tz = Timezone(utc=self.mTZUTC, tzid=self.mTZID)
        self.copy_ICalendarDateTime(self.getToday(tz))


    @staticmethod
    def getToday(tzid=None):
        # Get from posix time
        now = time.time()
        now_tm = time.localtime(now)

        temp = DateTime(year=now_tm.tm_year, month=now_tm.tm_mon, day=now_tm.tm_mday, tzid=tzid)
        return temp


    def setNow(self):
        tz = Timezone(utc=self.mTZUTC, tzid=self.mTZID)
        self.copy_ICalendarDateTime(self.getNow(tz))


    @staticmethod
    def getNow(tzid):
        utc = DateTime.getNowUTC()
        utc.adjustTimezone(tzid if tzid is not None else Timezone())
        return utc


    def setNowUTC(self):
        self.copy_DateTime(self.getNowUTC())


    @staticmethod
    def getNowUTC():
        # Get from posix time
        now = time.time()
        now_tm = time.gmtime(now)
        tzid = Timezone(utc=True)

        return DateTime(year=now_tm.tm_year, month=now_tm.tm_mon, day=now_tm.tm_mday, hours=now_tm.tm_hour, minutes=now_tm.tm_min, seconds=now_tm.tm_sec, tzid=tzid)


    def recur(self, freq, interval, allow_invalid=False):
        # Add appropriate interval
        normalize = True
        if freq == definitions.eRecurrence_SECONDLY:
            self.mSeconds += interval
        elif freq == definitions.eRecurrence_MINUTELY:
            self.mMinutes += interval
        elif freq == definitions.eRecurrence_HOURLY:
            self.mHours += interval
        elif freq == definitions.eRecurrence_DAILY:
            self.mDay += interval
        elif freq == definitions.eRecurrence_WEEKLY:
            self.mDay += 7 * interval
        elif freq == definitions.eRecurrence_MONTHLY:
            # Iterate until a valid day in the next month is found.
            # This can happen if adding one month to e.g. 31 January.
            # That is an undefined operation - does it mean 28/29 February
            # or 1/2 May, or 31 March or what? We choose to find the next month with
            # the same day number as the current one.
            self.mMonth += interval

            # Normalise month
            normalised_month = ((self.mMonth - 1) % 12) + 1
            adjustment_year = (self.mMonth - 1) / 12
            if (normalised_month - 1) < 0:
                normalised_month += 12
                adjustment_year -= 1
            self.mMonth = normalised_month
            self.mYear += adjustment_year

            if not allow_invalid:
                self.normalise()
                while self.mDay > utils.daysInMonth(self.mMonth, self.mYear):
                    self.mMonth += interval
                    self.normalise()
            normalize = False
        elif freq == definitions.eRecurrence_YEARLY:
            self.mYear += interval
            if allow_invalid:
                normalize = False

        if normalize:
            # Normalise to standard date-time ranges
            self.normalise()
        else:
            self.changed()


    def getLocaleDate(self, dateTimeFormat):

        buf = StringIO.StringIO()

        if dateTimeFormat == DateTime.FULLDATE:
            buf.write(locale.getDay(self.getDayOfWeek(), locale.LONG))
            buf.write(", ")
            buf.write(locale.getMonth(self.mMonth, locale.LONG))
            buf.write(" ")
            buf.write(str(self.mDay))
            buf.write(", ")
            buf.write(str(self.mYear))
        elif dateTimeFormat == DateTime.ABBREVDATE:
            buf.write(locale.getDay(self.getDayOfWeek(), locale.SHORT))
            buf.write(", ")
            buf.write(locale.getMonth(self.mMonth, locale.SHORT))
            buf.write(" ")
            buf.write(str(self.mDay))
            buf.write(", ")
            buf.write(str(self.mYear))
        elif dateTimeFormat == DateTime.NUMERICDATE:
            buf.write(str(self.mMonth))
            buf.write("/")
            buf.write(str(self.mDay))
            buf.write("/")
            buf.write(str(self.mYear))
        elif dateTimeFormat == DateTime.FULLDATENOYEAR:
            buf.write(locale.getDay(self.getDayOfWeek(), locale.LONG))
            buf.write(", ")
            buf.write(locale.getMonth(self.mMonth, locale.LONG))
            buf.write(" ")
            buf.write(str(self.mDay))
        elif dateTimeFormat == DateTime.ABBREVDATENOYEAR:
            buf.write(locale.getDay(self. getDayOfWeek(), locale.SHORT))
            buf.write(", ")
            buf.write(locale.getMonth(self.mMonth, locale.SHORT))
            buf.write(" ")
            buf.write(str(self.mDay))
        elif dateTimeFormat == DateTime.NUMERICDATENOYEAR:
            buf.write(str(self.mMonth))
            buf.write("/")
            buf.write(str(self.mDay))

        return buf.getvalue()


    def getTime(self, with_seconds, am_pm, tzid):

        buf = StringIO.StringIO()
        adjusted_hour = self.mHours

        if am_pm:
            am = True
            if adjusted_hour >= 12:
                adjusted_hour -= 12
                am = False

            if adjusted_hour == 0:
                adjusted_hour = 12

            buf.write(str(adjusted_hour))
            buf.write(":")
            if self.mMinutes < 10:
                buf.write("0")
            buf.write(str(self.mMinutes))
            if with_seconds:
                buf.write(":")
                if self.mSeconds < 10:
                    buf.write("0")
                buf.write(str(self.mSeconds))

            buf.write([" AM", " PM"][not am])
        else:
            if self.mHours < 10:
                buf.write("0")
            buf.write(str(self.mHours))
            buf.write(":")
            if self.mMinutes < 10:
                buf.write("0")
            buf.write(str(self.mMinutes))
            if with_seconds:
                buf.write(":")
                if self.mSeconds < 10:
                    buf.write("0")
                buf.write(str(self.mSeconds))

        if tzid:
            desc = self.timeZoneDescriptor()
            if len(desc) > 0:
                buf.write(" ")
                buf.write(desc)

        return buf.getvalue()


    def getLocaleDateTime(self, locale, with_seconds, am_pm, tzid):
        return self.getLocaleDate(locale) + " " + self.getTime(with_seconds, am_pm, tzid)


    def getText(self):

        if self.mDateOnly:
            return "%04d%02d%02d" % (self.mYear, self.mMonth, self.mDay)
        else:
            if self.mTZUTC:
                return "%04d%02d%02dT%02d%02d%02dZ" % (self.mYear, self.mMonth, self.mDay, self.mHours, self.mMinutes, self.mSeconds)
            elif isinstance(self.mTZID, int):
                sign = "-" if self.mTZID < 0 else "+"
                hours = abs(self.mTZID) / 3600
                minutes = divmod(abs(self.mTZID) / 60, 60)[1]
                return "%04d%02d%02dT%02d%02d%02d%s%02d%02d" % (self.mYear, self.mMonth, self.mDay, self.mHours, self.mMinutes, self.mSeconds, sign, hours, minutes)
            else:
                return "%04d%02d%02dT%02d%02d%02d" % (self.mYear, self.mMonth, self.mDay, self.mHours, self.mMinutes, self.mSeconds)


    def getXMLText(self):

        if self.mDateOnly:
            return "%04d-%02d-%02d" % (self.mYear, self.mMonth, self.mDay)
        else:
            if self.mTZUTC:
                return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (self.mYear, self.mMonth, self.mDay, self.mHours, self.mMinutes, self.mSeconds)
            elif isinstance(self.mTZID, int):
                sign = "-" if self.mTZID < 0 else "+"
                hours = abs(self.mTZID) / 3600
                minutes = divmod(abs(self.mTZID) / 60, 60)[1]
                return "%04d-%02d-%02dT%02d:%02d:%02d%s%02d:%02d" % (self.mYear, self.mMonth, self.mDay, self.mHours, self.mMinutes, self.mSeconds, sign, hours, minutes)
            else:
                return "%04d-%02d-%02dT%02d:%02d:%02d" % (self.mYear, self.mMonth, self.mDay, self.mHours, self.mMinutes, self.mSeconds)

    getJSONText = getXMLText

    @classmethod
    def parseText(cls, data, fullISO=False):
        dt = cls()
        dt.parse(data, fullISO)
        return dt


    def parseDate(self, data, fullISO):
        # Get year
        self.mYear = int(data[0:4])
        index = 4
        if fullISO and data[index] == "-":
            index += 1

        # Get month
        self.mMonth = int(data[index:index + 2])
        index += 2
        if fullISO and data[index] == "-":
            index += 1

        # Get day
        self.mDay = int(data[index:index + 2])
        index += 2

        if ' ' in data[:index] and ParserContext.INVALID_DATETIME_LEADINGSPACE == ParserContext.PARSER_RAISE:
            raise ValueError
        if self.mYear < 0 or self.mMonth < 0 or self.mDay < 0:
            raise ValueError
        return index


    def parseTime(self, data, index, fullISO):
        # Get hours
        self.mHours = int(data[index:index + 2])
        index += 2
        if fullISO and data[index] == ":":
            index += 1

        # Get minutes
        self.mMinutes = int(data[index:index + 2])
        index += 2
        if fullISO and data[index] == ":":
            index += 1

        # Get seconds
        self.mSeconds = int(data[index:index + 2])
        index += 2

        return index


    def parseFractionalAndUTCOffset(self, data, index, dlen):
        # Optional fraction
        if data[index] == ",":
            index += 1
            if not data[index].isdigit():
                raise ValueError
            while index < dlen and data[index].isdigit():
                index += 1

        # Optional timezone descriptor
        if index < dlen:
            if data[index] == "Z":
                index += 1
                self.mTZUTC = True
            else:
                if data[index] == "+":
                    sign = 1
                elif data[index] == "-":
                    sign = -1
                else:
                    raise ValueError
                index += 1

                # Get hours
                hours_offset = int(data[index:index + 2])
                index += 2
                if data[index] == ":":
                    index += 1

                # Get minutes
                minutes_offset = int(data[index:index + 2])
                index += 2

                self.mTZID = sign * (hours_offset * 60 + minutes_offset) * 60

        if index < dlen:
            raise ValueError
        return index


    def parse(self, data, fullISO=False):

        # iCalendar:
        #   parse format YYYYMMDD[THHMMSS[Z]]
        # vCard (fullISO), jCal
        #   parse format YYYY[-]MM[-]DD[THH[:]MM[:]SS[(Z/(+/-)HHMM]]

        try:
            # Parse out the date
            index = self.parseDate(data, fullISO)

            # Now look for more
            dlen = len(data)
            if index < dlen:

                if data[index] != 'T':
                    raise ValueError
                index += 1

                # Parse out the time
                index = self.parseTime(data, index, fullISO)
                self.mDateOnly = False

                if index < dlen:
                    if fullISO:
                        index = self.parseFractionalAndUTCOffset(data, index, dlen)
                    else:
                        if index < dlen:
                            if data[index] != 'Z':
                                raise ValueError
                            index += 1
                            self.mTZUTC = True
                            if index < dlen:
                                raise ValueError
                else:
                    self.mTZUTC = False
            else:
                self.mDateOnly = True
        except IndexError:
            raise ValueError

        # Always uncache posix time
        self.changed()


    def generate(self, os):
        try:
            os.write(self.getText())
        except:
            pass


    def generateRFC2822(self, os):
        pass


    def writeXML(self, node, namespace):
        value = XML.SubElement(
            node,
            xmlutils.makeTag(
                namespace,
                xmldefinitions.value_date if self.isDateOnly() else xmldefinitions.value_date_time
            )
        )
        value.text = self.getXMLText()


    def parseJSON(self, jobject):
        self.parse(str(jobject), True)


    def writeJSON(self, jobject):
        jobject.append(self.getJSONText())


    def invalid(self):
        """
        Are any of the current fields invalid.
        """

        # Right now we only care about invalid days of the month (e.g. February 30th). In the
        # future we may also want to look for invalid times during a DST transition.

        if self.mDay <= 0 or self.mDay > utils.daysInMonth(self.mMonth, self.mYear):
            return True

        return False


    def normalise(self):
        # Normalise seconds
        normalised_secs = self.mSeconds % 60
        adjustment_mins = self.mSeconds / 60
        if normalised_secs < 0:
            normalised_secs += 60
            adjustment_mins -= 1
        self.mSeconds = normalised_secs
        self.mMinutes += adjustment_mins

        # Normalise minutes
        normalised_mins = self.mMinutes % 60
        adjustment_hours = self.mMinutes / 60
        if normalised_mins < 0:
            normalised_mins += 60
            adjustment_hours -= 1
        self.mMinutes = normalised_mins
        self.mHours += adjustment_hours

        # Normalise hours
        normalised_hours = self.mHours % 24
        adjustment_days = self.mHours / 24
        if normalised_hours < 0:
            normalised_hours += 24
            adjustment_days -= 1
        self.mHours = normalised_hours
        self.mDay += adjustment_days

        # Wipe the time if date only
        if self.mDateOnly:
            self.mSeconds = self.mMinutes = self.mHours = 0

        # Adjust the month first, since the day adjustment is month dependent

        # Normalise month
        normalised_month = ((self.mMonth - 1) % 12) + 1
        adjustment_year = (self.mMonth - 1) / 12
        if (normalised_month - 1) < 0:
            normalised_month += 12
            adjustment_year -= 1
        self.mMonth = normalised_month
        self.mYear += adjustment_year

        # Now do days
        if self.mDay > 0:
            while self.mDay > utils.daysInMonth(self.mMonth, self.mYear):
                self.mDay -= utils.daysInMonth(self.mMonth, self.mYear)
                self.mMonth += 1
                if self.mMonth > 12:
                    self.mMonth = 1
                    self.mYear += 1
        else:
            while self.mDay <= 0:
                self.mMonth -= 1
                if self.mMonth < 1:
                    self.mMonth = 12
                    self.mYear -= 1
                self.mDay += utils.daysInMonth(self.mMonth, self.mYear)

        # Always invalidate posix time cache
        self.changed()


    def timeZoneSecondsOffset(self, relative_to_utc=False):
        if self.mTZUTC:
            return 0
        if self.mTZOffset is None:
            tz = Timezone(utc=self.mTZUTC, tzid=self.mTZID)
            self.mTZOffset = tz.timeZoneSecondsOffset(self, relative_to_utc)
        return self.mTZOffset


    def timeZoneDescriptor(self):
        tz = Timezone(utc=self.mTZUTC, tzid=self.mTZID)
        return tz.timeZoneDescriptor(self)


    def changed(self):
        self.mPosixTimeCached = False
        self.mTZOffset = None


    def daysSince1970(self):
        # Add days between 1970 and current year (ignoring leap days)
        result = (self.mYear - 1970) * 365

        # Add leap days between years
        result += utils.leapDaysSince1970(self.mYear - 1970)

        # Add days in current year up to current month (includes leap day for
        # current year as needed)
        result += utils.daysUptoMonth(self.mMonth, self.mYear)

        # Add days in month
        result += self.mDay - 1

        return result
