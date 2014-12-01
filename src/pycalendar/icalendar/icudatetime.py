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

from cffi import FFI
from __builtin__ import classmethod
from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions

# Use cffi to get access to libicucore functions and constants
ffi = FFI()
hdr = """
    //#define U_FAILURE(x) ((x)>U_ZERO_ERROR)

    typedef double UDate;
    UDate     ucal_getNow (void);

    typedef void *        UCalendar;
    typedef uint16_t    UChar;
    enum      UCalendarType { UCAL_TRADITIONAL=0, UCAL_DEFAULT=0, UCAL_GREGORIAN, ... };
    typedef enum UCalendarType UCalendarType;
    enum UErrorCode {
        U_ZERO_ERROR = 0
    };
    typedef enum UErrorCode UErrorCode;

    enum UCalendarDaysOfWeek {
      /** Sunday */
      UCAL_SUNDAY = 1,
      /** Monday */
      UCAL_MONDAY,
      /** Tuesday */
      UCAL_TUESDAY,
      /** Wednesday */
      UCAL_WEDNESDAY,
      /** Thursday */
      UCAL_THURSDAY,
      /** Friday */
      UCAL_FRIDAY,
      /** Saturday */
      UCAL_SATURDAY
    };

    typedef enum UCalendarDaysOfWeek UCalendarDaysOfWeek;

    enum UCalendarDateFields {
      UCAL_ERA,
      UCAL_YEAR,
      UCAL_MONTH,
      UCAL_WEEK_OF_YEAR,
      UCAL_WEEK_OF_MONTH,
      UCAL_DATE,
      UCAL_DAY_OF_YEAR,
      UCAL_DAY_OF_WEEK,
      UCAL_DAY_OF_WEEK_IN_MONTH,
      UCAL_AM_PM,
      UCAL_HOUR,
      UCAL_HOUR_OF_DAY,
      UCAL_MINUTE,
      UCAL_SECOND,
      UCAL_MILLISECOND,
      UCAL_ZONE_OFFSET,
      UCAL_DST_OFFSET,
      UCAL_YEAR_WOY,
      UCAL_DOW_LOCAL,
      UCAL_EXTENDED_YEAR,
      UCAL_JULIAN_DAY,
      UCAL_MILLISECONDS_IN_DAY,
      UCAL_IS_LEAP_MONTH,
      UCAL_FIELD_COUNT,
      UCAL_DAY_OF_MONTH=5
      };

    typedef enum UCalendarDateFields UCalendarDateFields;

    enum UCalendarMonths {
      /** January */
      UCAL_JANUARY,
      /** February */
      UCAL_FEBRUARY,
      /** March */
      UCAL_MARCH,
      /** April */
      UCAL_APRIL,
      /** May */
      UCAL_MAY,
      /** June */
      UCAL_JUNE,
      /** July */
      UCAL_JULY,
      /** August */
      UCAL_AUGUST,
      /** September */
      UCAL_SEPTEMBER,
      /** October */
      UCAL_OCTOBER,
      /** November */
      UCAL_NOVEMBER,
      /** December */
      UCAL_DECEMBER,
      /** Value of the <code>UCAL_MONTH</code> field indicating the
        * thirteenth month of the year. Although the Gregorian calendar
        * does not use this value, lunar calendars do.
        */
      UCAL_UNDECIMBER
    };
    typedef enum UCalendarMonths UCalendarMonths;

    UCalendar * ucal_open(const UChar *zoneID, int32_t len, const char *locale, UCalendarType type, UErrorCode *status);
    void        ucal_close(UCalendar *cal);
    UCalendar * ucal_clone(const UCalendar* cal, UErrorCode* status);
    void        ucal_setDate(UCalendar *cal, int32_t year, int32_t month, int32_t date, UErrorCode *status);

    const char* ucal_getTZDataVersion (UErrorCode *status);

    UDate ucal_getMillis(const UCalendar* cal,
               UErrorCode* status);
    void  ucal_setMillis(UCalendar* cal,
               UDate        dateTime,
               UErrorCode*  status);

    int32_t ucal_get(const UCalendar* cal,
         UCalendarDateFields  field,
         UErrorCode*          status);
    void ucal_set(UCalendar*  cal,
         UCalendarDateFields  field,
         int32_t              value);
    void ucal_add(UCalendar*  cal,
         UCalendarDateFields  field,
         int32_t              amount,
         UErrorCode*          status);

    enum UCalendarLimitType {
      /** Minimum value */
      UCAL_MINIMUM,
      /** Maximum value */
      UCAL_MAXIMUM,
      /** Greatest minimum value */
      UCAL_GREATEST_MINIMUM,
      /** Leaest maximum value */
      UCAL_LEAST_MAXIMUM,
      /** Actual minimum value */
      UCAL_ACTUAL_MINIMUM,
      /** Actual maximum value */
      UCAL_ACTUAL_MAXIMUM
    };

    typedef enum UCalendarLimitType UCalendarLimitType;

    int32_t ucal_getLimit(const UCalendar*     cal,
                  UCalendarDateFields  field,
                  UCalendarLimitType   type,
                  UErrorCode*          status);
"""

ffi.cdef(hdr)
ffi.verify(hdr.replace(", ...", ""))

ICU = ffi.dlopen("libicucore")

class ICUDateTime(object):
    """
    An ICU-based L{DateTime} like class that supports non-Gregorian date-time values and arithmetic.
    """

    RSCALE_GREGORIAN = "gregorian"
    RSCALE_HEBREW = "hebrew"

    RSCALE_CALCODE = {
        "gregorian": "",
        "chinese": "C",
        "islamic-civil": "I",
        "hebrew": "H",
        "ethiopic": "E",
    }

    def __init__(self, rscale, ucal):
        """
        Initialize using an ICU C{ucal} object and the name of the calendar scale.

        @param rscale: calendar scale being used
        @type rscale: L{str}
        @param ucal: ICU ucal object
        @type ucal: L{ICU.UCalendar*}
        """
        self.rscale = rscale
        self.ucal = ucal

        self.mHours = 0
        self.mMinutes = 0
        self.mSeconds = 0

        self.mDateOnly = True

        self.mTZUTC = False
        self.mTZID = None
        self.mTZOffset = None

        self.mInvalid = None


    def __del__(self):
        """
        Always close the ICU C{ucal} object.
        """
        ICU.ucal_close(self.ucal)
        self.ucal = None


    def duplicate(self):
        """
        Duplicate this object.
        """

        error = ffi.new("UErrorCode *", 0)
        clone = ICU.ucal_clone(self.ucal, error)
        dup = ICUDateTime(self.rscale, clone)
        dup._transferHHMMSS(self, dup)
        dup.mInvalid = self.mInvalid

        return dup


    def __repr__(self):
        return "ICUDateTime: %s" % (self.getText(),)


    def __hash__(self):
        return hash(self.getPosixTime())


    @classmethod
    def fromDateTime(cls, dt, rscale):
        """
        Convert from a regular L{DateTime} to the specified calendar scale.

        @param dt: the regular value to convert from
        @type dt: L{DateTime}
        @param rscale: the calendar scale to convert to
        @type rscale: L{str}

        @return: the new ICU object
        @rtyope: L{ICUDateTime}
        """

        # Try to create the ICU object that represents this date
        gregorian = cls.fromDateComponents(cls.RSCALE_GREGORIAN, dt.getYear(), dt.getMonth(), dt.getDay())
        cls._transferHHMMSS(dt, gregorian)
        return gregorian.convertTo(rscale)


    def toDateTime(self):
        """
        Convert to a regular L{DateTime}.

        @return: the converted object
        @rtype: L{DateTime}
        """

        # Try to create the ICU object that represents this date
        gregorian = self if self.rscale.lower() == self.RSCALE_GREGORIAN else self.convertTo(self.RSCALE_GREGORIAN)
        dt = DateTime(gregorian.getYear(), gregorian.getMonth(), gregorian.getDay())
        self._transferHHMMSS(self, dt)
        return dt


    @classmethod
    def _newUcal(cls, rscale):
        """
        Create an ICU C{ucal} object for the specified calendar scale.

        @param rscale: calendar scale to use
        @type rscale: L{str}

        @return: the ICU ucal object
        @rtype: L{ICU.UCalendar*}
        """
        calsystem = "*@calendar={}".format(rscale)
        error = ffi.new("UErrorCode *", 0)
        ucal = ICU.ucal_open(ffi.NULL, -1, ffi.new("char[]", calsystem), ICU.UCAL_DEFAULT, error)
        if error[0] != ICU.U_ZERO_ERROR:
            raise ValueError("Unable to create ICU calendar for rscale '{}', code: {}".format(rscale, error))
        return ucal


    @classmethod
    def fromDateComponents(cls, rscale, year, month, day, isleapmonth=False):
        """
        Create ICU calendar for the specified calendar scale with the specified components.

        @param dt: the regular value to convert from
        @type dt: L{DateTime}
        @param rscale: the calendar scale to convert to
        @type rscale: L{str}
        @param year: the year component
        @type year: L{int}
        @param month: the month component
        @type month: L{int}
        @param day: the day component
        @type day: L{int}
        @param isleapmonth: the leap month component
        @type isleapmonth: L{bool}

        @return: the new object
        @rtype: L{ICUDateTime}
        """

        # Try to create the ICU object that represents this date
        ucal = cls._newUcal(rscale)

        month, isleapmonth = cls._adjustToICULeapMonth(rscale, month, isleapmonth)

        ICU.ucal_set(ucal, ICU.UCAL_EXTENDED_YEAR, year)
        ICU.ucal_set(ucal, ICU.UCAL_MONTH, cls._numericMonthToICU(month))
        ICU.ucal_set(ucal, ICU.UCAL_DAY_OF_MONTH, day)
        ICU.ucal_set(ucal, ICU.UCAL_IS_LEAP_MONTH, isleapmonth)

        return ICUDateTime(rscale, ucal)


    @classmethod
    def _numericMonthToICU(cls, month):
        """
        Map our month numbers (1..13) to ICU constants.

        @param month: the month to map
        @type month: L{int}

        @return: the ICU constant
        @rtype: L{ICU.UCalendarMonths}
        """
        return {
            1: ICU.UCAL_JANUARY,
            2: ICU.UCAL_FEBRUARY,
            3: ICU.UCAL_MARCH,
            4: ICU.UCAL_APRIL,
            5: ICU.UCAL_MAY,
            6: ICU.UCAL_JUNE,
            7: ICU.UCAL_JULY,
            8: ICU.UCAL_AUGUST,
            9: ICU.UCAL_SEPTEMBER,
            10: ICU.UCAL_OCTOBER,
            11: ICU.UCAL_NOVEMBER,
            12: ICU.UCAL_DECEMBER,
            13: ICU.UCAL_UNDECIMBER,
        }[month]


    @classmethod
    def _icuToNumericMonth(cls, month):
        """
        Map ICU constants to our month numbers (1..13).

        @param month: the ICU constant to map
        @type month: L{ICU.UCalendarMonths}

        @return: the month
        @rtype: L{int}
        """
        return {
            ICU.UCAL_JANUARY: 1,
            ICU.UCAL_FEBRUARY: 2,
            ICU.UCAL_MARCH: 3,
            ICU.UCAL_APRIL: 4,
            ICU.UCAL_MAY: 5,
            ICU.UCAL_JUNE: 6,
            ICU.UCAL_JULY: 7,
            ICU.UCAL_AUGUST: 8,
            ICU.UCAL_SEPTEMBER: 9,
            ICU.UCAL_OCTOBER: 10,
            ICU.UCAL_NOVEMBER: 11,
            ICU.UCAL_DECEMBER: 12,
            ICU.UCAL_UNDECIMBER: 13,
        }[month]


    @classmethod
    def _adjustToICULeapMonth(cls, rscale, month, isleapmonth):
        """
        For the Hebrew calendar, ICU uses a count of 13 months rather than 12 months
        plus an "isleapmonth" indicator. So when converting to/from ICU we need to make
        that adjustment as we always use 12 months + isleapmonth. This method converts
        from our internal representation to what ICU uses.

        @param rscale: calendar scale to convert to
        @type rscale: L{str}
        @param month: month number (12 month cycle)
        @type month: L{int}
        @param isleapmonth: is leap month indicator
        @type isleapmonth: L{bool} of L{None}

        @return: a tuple of the ICU-mapped month number and isleapmonth indicator
        @rtype: L{tuple} of (L{int}, L{bool}
        """

        if rscale.lower() == cls.RSCALE_HEBREW:
            if month == 5 and isleapmonth:
                month = 6
                isleapmonth = None
            elif month >= 6:
                month += 1
        return (month, isleapmonth,)


    @classmethod
    def _adjustFromICULeapMonth(cls, rscale, month, isleapmonth):
        """
        For the Hebrew calendar, ISU uses a count of 13 months rather than 12 months
        plus an "isleapmonth" indicator. So when converting to/from ICU we need to make
        that adjustment as we always use 12 months + isleapmonth. This method converts
        to our internal representation from what ICU uses.

        @param rscale: calendar scale to convert from
        @type rscale: L{str}
        @param month: month number (13 month cycle)
        @type month: L{int}
        @param isleapmonth: is leap month indicator
        @type isleapmonth: L{bool} of L{None}

        @return: a tuple of the month number and isleapmonth indicator
        @rtype: L{tuple} of (L{int}, L{bool}
        """

        if rscale.lower() == cls.RSCALE_HEBREW:
            isleapmonth = False
            if month == 6:
                isleapmonth = True
            elif month >= 6:
                month -= 1
        return (month, isleapmonth,)


    @classmethod
    def _transferHHMMSS(cls, from_dt, to_dt):
        """
        Transfer the time and timezone components from one L{ICUDateTime} to another.

        @param from_dt: object to copy from
        @type from_dt: L{ICUDateTime}
        @param to_dt: object to copy to
        @type to_dt: L{ICUDateTime}
        """
        if not from_dt.isDateOnly():
            to_dt.setDateOnly(False)
            to_dt.setHHMMSS(from_dt.getHours(), from_dt.getMinutes(), from_dt.getSeconds())
            to_dt.setTimezoneID(from_dt.getTimezoneID())
            to_dt.setTimezoneUTC(from_dt.getTimezoneUTC())


    def convertTo(self, rscale):
        """
        Convert this L{ICUDateTime} into another one in the specified calendar scale.

        @param rscale: calendar scale to convert to
        @type rscale: L{str}

        @return: the converted date
        @rtype: L{ICUDateTime}
        """
        error = ffi.new("UErrorCode *", 0)
        converted = self._newUcal(rscale)
        millis = ICU.ucal_getMillis(self.ucal, error)
        ICU.ucal_setMillis(converted, millis, error)
        dt = ICUDateTime(rscale, converted)
        self._transferHHMMSS(self, dt)

        # For some reason this is needed to properly setup all the fields. Without this, I have
        # noticed that ucal_getLimit does not return the correct day of month limit for a Chinese
        # calendar.
        dt.getDateComponents()

        return dt


    def getDateComponents(self):
        """
        Get the year, month, day, isleapmonth components in our internal format from
        this ICU date.

        @return: the date components
        @rtype: L{tuple} of (L{int}, L{int}, L{int}, L{bool})
        """
        year = self.getYear()
        month = self.getMonth()
        day = self.getDay()
        isleapmonth = self.getLeapMonth()

        month, isleapmonth = self._adjustFromICULeapMonth(self.rscale, month, isleapmonth)

        return (year, month, day, isleapmonth,)


    def getPosixTime(self):
        """
        Return an integer representing a standard offset in seconds from a specific
        epoch. This is used for sorting similar object.
        """

        # Use the ICU "millis" for this.
        error = ffi.new("UErrorCode *", 0)
        return ICU.ucal_getMillis(self.ucal, error)


    def isDateOnly(self):
        return self.mDateOnly


    def setDateOnly(self, date_only):
        self.mDateOnly = date_only


    def setYYMMDD(self, year, month, day, isleapmonth=False):
        self.setYear(year)
        self.setMonth(month, isleapmonth)
        self.setDay(day)

        self.testInvalid(year, month, day, isleapmonth)


    def getYear(self):
        error = ffi.new("UErrorCode *", 0)
        return ICU.ucal_get(self.ucal, ICU.UCAL_EXTENDED_YEAR, error)


    def setYear(self, year):
        _ignore_old_year, old_month, old_day, old_isleapmonth = self.getDateComponents()
        ICU.ucal_set(self.ucal, ICU.UCAL_EXTENDED_YEAR, year)
        self.testInvalid(year, old_month, old_day, old_isleapmonth)


    def offsetYear(self, diff_year):
        """
        Offset the ICU date year component by the specified amount.

        @param diff_year: amount to offset
        @type diff_year: L{int}
        """
        error = ffi.new("UErrorCode *", 0)
        ICU.ucal_add(self.ucal, ICU.UCAL_EXTENDED_YEAR, diff_year, error)


    def getMonth(self):
        error = ffi.new("UErrorCode *", 0)
        return self._icuToNumericMonth(ICU.ucal_get(self.ucal, ICU.UCAL_MONTH, error))


    def setMonth(self, month, isleapmonth=False):
        old_year, _ignore_old_month, old_day, _ignore_old_isleapmonth = self.getDateComponents()
        ICU.ucal_set(self.ucal, ICU.UCAL_MONTH, self._numericMonthToICU(month))
        ICU.ucal_set(self.ucal, ICU.UCAL_IS_LEAP_MONTH, isleapmonth)
        self.testInvalid(old_year, month, old_day, isleapmonth)


    def offsetMonth(self, diff_month):
        """
        Offset the ICU date month component by the specified amount.

        @param diff_year: amount to offset
        @type diff_year: L{int}
        """
        error = ffi.new("UErrorCode *", 0)
        ICU.ucal_add(self.ucal, ICU.UCAL_MONTH, diff_month, error)


    def getLeapMonth(self):
        error = ffi.new("UErrorCode *", 0)
        return ICU.ucal_get(self.ucal, ICU.UCAL_IS_LEAP_MONTH, error) != 0


    def getDay(self):
        error = ffi.new("UErrorCode *", 0)
        return ICU.ucal_get(self.ucal, ICU.UCAL_DAY_OF_MONTH, error)


    def setDay(self, day):
        old_year, old_month, _ignore_old_day, old_isleapmonth = self.getDateComponents()
        ICU.ucal_set(self.ucal, ICU.UCAL_DAY_OF_MONTH, day)
        self.testInvalid(old_year, old_month, day, old_isleapmonth)


    def offsetDay(self, diff_day):
        """
        Offset the ICU date month component by the specified amount.

        @param diff_year: amount to offset
        @type diff_year: L{int}
        """
        error = ffi.new("UErrorCode *", 0)
        ICU.ucal_add(self.ucal, ICU.UCAL_DAY_OF_MONTH, diff_day, error)


    def setYearDay(self, day, allow_invalid=False):

        # Find the limit for the current year
        error = ffi.new("UErrorCode *", 0)
        limit = ICU.ucal_getLimit(self.ucal, ICU.UCAL_DAY_OF_YEAR, ICU.UCAL_ACTUAL_MAXIMUM, error)

        if day > 0:
            ICU.ucal_set(self.ucal, ICU.UCAL_DAY_OF_YEAR, min(day, limit))
            if day > limit and allow_invalid:
                self.setInvalid(self.getYear(), 1, day)
            else:
                self.clearInvalid()
        elif day < 0:
            offset = limit + day + 1
            ICU.ucal_set(self.ucal, ICU.UCAL_DAY_OF_YEAR, max(offset, 1))
            if offset <= 0 and allow_invalid:
                self.setInvalid(self.getYear(), 1, day)
            else:
                self.clearInvalid()


    def getYearDay(self):
        error = ffi.new("UErrorCode *", 0)
        return ICU.ucal_get(self.ucal, ICU.UCAL_DAY_OF_YEAR, error)


    def setMonthDay(self, day, allow_invalid=False):

        # Find the limit for the current year
        error = ffi.new("UErrorCode *", 0)
        limit = ICU.ucal_getLimit(self.ucal, ICU.UCAL_DAY_OF_MONTH, ICU.UCAL_ACTUAL_MAXIMUM, error)

        if day > 0:
            ICU.ucal_set(self.ucal, ICU.UCAL_DAY_OF_MONTH, min(day, limit))
            if day > limit and allow_invalid:
                y, m, _ignore_d, l = self.getDateComponents()
                self.setInvalid(y, m, day, l)
            else:
                self.clearInvalid()

        elif day < 0:
            offset = limit + day + 1
            ICU.ucal_set(self.ucal, ICU.UCAL_DAY_OF_MONTH, max(offset, 1))
            if offset <= 0 and allow_invalid:
                y, m, _ignore_d, l = self.getDateComponents()
                self.setInvalid(y, m, day, l)
            else:
                self.clearInvalid()


    def isMonthDay(self, day):
        if day > 0:
            return self.getDay() == day
        elif day < 0:
            error = ffi.new("UErrorCode *", 0)
            limit = ICU.ucal_getLimit(self.ucal, ICU.UCAL_DAY_OF_MONTH, ICU.UCAL_ACTUAL_MAXIMUM, error)
            return self.getDay() - 1 - limit == day
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

        # Only supported for Gregorian calendars
        if self.rscale.lower() != self.RSCALE_GREGORIAN:
            raise ValueError("Week numbers only supported for Gregorian calendars")
        dt = self.toDateTime()
        dt.setWeekNo(weekno)
        self.setYYMMDD(dt.getYear(), dt.getMonth(), dt.getDay())


    def getWeekNo(self):
        """
        Return the ISO week number for the current date.
        """

        # Only supported for Gregorian calendars
        if self.rscale.lower() != self.RSCALE_GREGORIAN:
            raise ValueError("Week numbers only supported for Gregorian calendars")
        dt = self.toDateTime()
        return dt.getWeekNo()


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
        self.setYYMMDD(self.getYear(), 1, 1, False)

        # Determine first weekday in year
        first_day = self.getDayOfWeek()

        if offset > 0:
            cycle = (offset - 1) * 7 + day
            cycle -= first_day
            if first_day > day:
                cycle += 7
            self.offsetDay(cycle)
        elif offset < 0:
            # Find the limit for the current year
            error = ffi.new("UErrorCode *", 0)
            limit = ICU.ucal_getLimit(self.ucal, ICU.UCAL_DAY_OF_YEAR, ICU.UCAL_ACTUAL_MAXIMUM, error)

            first_day += limit - 1
            first_day %= 7

            cycle = (-offset - 1) * 7 - day
            cycle += first_day
            if day > first_day:
                cycle += 7
            self.offsetDay(limit - cycle - 1)

        self.clearInvalid()


    def setDayOfWeekInMonth(self, offset, day, allow_invalid=False):
        # Set to first day in month
        y, m, d, l = self.getDateComponents()
        self.setYYMMDD(y, m, 1, l)

        # Determine first weekday in month
        first_day = self.getDayOfWeek()

        if offset > 0:
            cycle = (offset - 1) * 7 + day
            cycle -= first_day
            if first_day > day:
                cycle += 7
            mday = cycle + 1
            self.offsetDay(cycle)
        elif offset < 0:
            # Find the limit for the current year
            error = ffi.new("UErrorCode *", 0)
            days_in_month = ICU.ucal_getLimit(self.ucal, ICU.UCAL_DAY_OF_MONTH, ICU.UCAL_ACTUAL_MAXIMUM, error)

            first_day += days_in_month - 1
            first_day %= 7

            cycle = (-offset - 1) * 7 - day
            cycle += first_day
            if day > first_day:
                cycle += 7
            mday = days_in_month - cycle
            self.offsetDay(days_in_month - cycle - 1)

        if self.getDay() != mday and allow_invalid:
            self.setInvalid(y, m, d, l)
        else:
            self.clearInvalid()


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
        return self.getDateComponents() == temp.getDateComponents()


    def getDayOfWeek(self):
        error = ffi.new("UErrorCode *", 0)
        return ICU.ucal_get(self.ucal, ICU.UCAL_DAY_OF_WEEK, error) - 1


    def setHHMMSS(self, hours, minutes, seconds):
        if (self.mHours != hours) or (self.mMinutes != minutes) or (self.mSeconds != seconds):
            self.mHours = hours
            self.mMinutes = minutes
            self.mSeconds = seconds


    def getHours(self):
        return self.mHours


    def setHours(self, hours):
        if self.mHours != hours:
            self.mHours = hours


    def offsetHours(self, diff_hour):
        self.mHours += diff_hour
        self.normalise()


    def getMinutes(self):
        return self.mMinutes


    def setMinutes(self, minutes):
        if self.mMinutes != minutes:
            self.mMinutes = minutes


    def offsetMinutes(self, diff_minutes):
        self.mMinutes += diff_minutes
        self.normalise()


    def getSeconds(self):
        return self.mSeconds


    def setSeconds(self, seconds):
        if self.mSeconds != seconds:
            self.mSeconds = seconds


    def offsetSeconds(self, diff_seconds):
        self.mSeconds += diff_seconds
        self.normalise()


    def getTimezoneUTC(self):
        return self.mTZUTC


    def setTimezoneUTC(self, utc):
        if self.mTZUTC != utc:
            self.mTZUTC = utc


    def getTimezoneID(self):
        return self.mTZID


    def setTimezoneID(self, tzid):
        self.mTZUTC = False
        self.mTZID = tzid


    # When doing recurrence iteration we sometimes need to preserve an invalid value for
    # either day or month (though month is never invalid for Gregorian calendars it can
    # be for non-Gregorian). For this class we simply set the stored attributes to their
    # invalid values.
    def setInvalid(self, year, month, day, isleapmonth=False):
        self.mInvalid = (year, month, day, isleapmonth,)


    def testInvalid(self, year, month, day, isleapmonth=False):
        """
        If the requested set of YYMMDDLL does not match the current set of YYMMDDLL then the requested
        set was invalid.
        """
        components = self.getDateComponents()
        if components != (year, month, day, isleapmonth,):
            self.setInvalid(year, month, day, isleapmonth)
        else:
            self.clearInvalid()


    def clearInvalid(self):
        self.mInvalid = None


    def invalid(self):
        """
        Are any of the current fields invalid.
        """

        # Right now we only care about invalid days of the month (e.g. February 30th). In the
        # future we may also want to look for invalid times during a DST transition.

        return self.mInvalid is not None


    def invalidSkip(self, skip):
        """
        If this is an invalid value skip backward or forward or not at all.

        @param skip: the skip mode (yes, backward, forward)
        @type skip: L{int}
        """

        if self.mInvalid:
            if skip == definitions.eRecurrence_SKIP_YES:
                # Leave it as invalid
                pass
            else:
                # Need to determine which component (day or month/leap) is invalid,
                # and react accordingly
                _ignore_y, m, d, l = self.getDateComponents()
                if (m, l) != (self.mInvalid[1], self.mInvalid[3]):
                    # Month/leap is invalid
                    if skip == definitions.eRecurrence_SKIP_BACKWARD:
                        # Defaults to skip backward
                        pass
                    elif skip == definitions.eRecurrence_SKIP_FORWARD:
                        self.offsetDay(1)

                elif d != self.mInvalid[2]:
                    if skip == definitions.eRecurrence_SKIP_BACKWARD:
                        if self.mInvalid[2] < 1:
                            self.offsetDay(-1)
                    elif skip == definitions.eRecurrence_SKIP_FORWARD:
                        if self.mInvalid[2] > 0:
                            self.offsetDay(1)

                self.clearInvalid()


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

        self.offsetDay(adjustment_days)

        # Wipe the time if date only
        if self.mDateOnly:
            self.mSeconds = self.mMinutes = self.mHours = 0


    def getText(self):
        """
        Generate an ISO-8601 string representation of this ICU date. Use a code
        prefix for the calendar scale.

        @return: the ISO-8601 text
        @rtype L{str}
        """
        calcode = self.RSCALE_CALCODE.get(self.rscale.lower(), "{}:".format(self.rscale))
        if calcode:
            calcode = "{{{}}}".format(calcode)
        year, month, day, isleapmonth = self.getDateComponents()
        date = "{}{:04d}{:02d}{}{:02d}".format(calcode, year, month, "L" if isleapmonth else "", day)
        if not self.isDateOnly():
            date += "T{:02d}{:02d}{:02d}{}".format(self.mHours, self.mMinutes, self.mSeconds, "Z" if self.mTZUTC else "")
        return date


if __name__ == '__main__':
    newyear = ICUDateTime.fromDateComponents("chinese", 4651, 1, 1, False)
    print("From: {} to {}".format(
        newyear.getText(),
        newyear.convertTo("gregorian").getText(),
    ))

    for i in range(0):
        newyear.offsetDay(1)
        print("From: {} to {}".format(
            newyear.getText(),
            newyear.convertTo("gregorian").getText(),
        ))

    offset = 1
    greg = ICUDateTime.fromDateComponents("gregorian", 2014, 1, 31, False)
    greg.offsetMonth(offset)
    print(greg.getText())

    greg = DateTime(2014, 1, 31)
    greg.offsetMonth(offset)
    print(greg.getText())
