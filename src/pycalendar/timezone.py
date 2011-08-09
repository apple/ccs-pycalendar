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

class PyCalendarTimezone(object):
    """
    Wrapper around a timezone specification. There are three options:
    
    UTC - when mUTC is True
    TZID - when mUTC is False and tzid is a str
    UTCOFFSET - when mUTC is False and tzid is an int
    """
    
    def __init__(self, utc=None, tzid=None):
        
        if utc is not None:
            self.mUTC = utc
            self.mTimezone = tzid
        elif tzid is not None:
            self.mUTC = tzid.lower() == 'utc'
            self.mTimezone = None if tzid.lower() == 'utc' else tzid
        else:
            self.mUTC = True
            self.mTimezone = None
    
            # Copy default timezone if it exists
            from manager import PyCalendarManager
            if PyCalendarManager.sICalendarManager is not None:
                defaulttz = PyCalendarManager.sICalendarManager.getDefaultTimezone()
                self.mUTC = defaulttz.mUTC
                self.mTimezone = defaulttz.mTimezone

    def duplicate(self):
        return PyCalendarTimezone(self.mUTC, self.mTimezone)

    def equals(self, comp):
        # Always match if any one of them is 'floating'
        if self.floating() or comp.floating():
            return True
        elif self.mUTC != comp.mUTC:
            return False
        else:
            return self.mUTC or stringutils.compareStringsSafe(self.mTimezone, comp.mTimezone)

    @staticmethod
    def same(utc1, tzid1, utc2, tzid2):
        # Always match if any one of them is 'floating'
        if PyCalendarTimezone.is_float(utc1, tzid1) or PyCalendarTimezone.is_float(utc2, tzid2):
            return True
        elif utc1 != utc2:
            return False
        else:
            return utc1 or stringutils.compareStringsSafe(tzid1, tzid2)

    @staticmethod
    def is_float(utc, tzid):
        return not utc and not tzid

    def getUTC(self):
        return self.mUTC

    def setUTC(self, utc):
        self.mUTC = utc

    def getTimezoneID(self):
        return self.mTimezone

    def setTimezoneID(self, tzid):
        self.mTimezone = tzid

    def floating(self):
        return not self.mUTC and self.mTimezone is None

    def hasTZID(self):
        return not self.mUTC and self.mTimezone is not None

    def timeZoneSecondsOffset(self, dt):
        from manager import PyCalendarManager
        from timezonedb import PyCalendarTimezoneDatabase
        if self.mUTC:
            return 0
        elif self.mTimezone is None:
            return PyCalendarTimezoneDatabase.getTimezoneOffsetSeconds(PyCalendarManager.sICalendarManager.getDefaultTimezone().getTimezoneID(), dt)
        elif isinstance(self.mTimezone, int):
            return self.mTimezone
        else:
            # Look up timezone and resolve date using default timezones
            return PyCalendarTimezoneDatabase.getTimezoneOffsetSeconds(self.mTimezone, dt)

    def timeZoneDescriptor(self, dt):
        from manager import PyCalendarManager
        from timezonedb import PyCalendarTimezoneDatabase
        if self.mUTC:
            return "(UTC)"
        elif self.mTimezone is None:
            return PyCalendarTimezoneDatabase.getTimezoneDescriptor(PyCalendarManager.sICalendarManager.getDefaultTimezone().getTimezoneID(), dt)
        elif isinstance(self.mTimezone, int):
            sign = "-" if self.mTimezone < 0 else "+"
            hours = abs(self.mTimezone) / 3600
            minutes = divmod(abs(self.mTimezone) / 60, 60)[1]
            return "%s%02d%02d" % (sign, hours, minutes,)
        else:
            # Look up timezone and resolve date using default timezones
            return PyCalendarTimezoneDatabase.getTimezoneDescriptor(self.mTimezone, dt)
    