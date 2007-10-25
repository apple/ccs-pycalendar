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

import stringutils

class PyCalendarTimezone(object):
    
    def __init__(self, utc=None, tzid=None, copyit=None):
        
        if utc:
            self.mUTC = utc
            self.mTimezone = tzid
        elif copyit:
            self._copy_PyCalendarTimezone(copyit)
        else:
            self.mUTC = True
            self.mTimezone = None
    
            # Copy defauilt timezone if it exists
            from manager import PyCalendarManager
            if PyCalendarManager.sICalendarManager is not None:
                self._copy_PyCalendarTimezone(PyCalendarManager.sICalendarManager.getDefaultTimezone())

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
        return not self.mUTC and not self.mTimezone

    def hasTZID(self):
        return not self.mUTC and self.mTimezone

    def timeZoneSecondsOffset(self, dt):
        from manager import PyCalendarManager
        from calendar import PyCalendar
        if self.mUTC:
            return 0
        elif not self.mTimezone:
            return PyCalendar.sICalendar.getTimezoneOffsetSeconds(PyCalendarManager.sICalendarManager.getDefaultTimezone().getTimezoneID(), dt)

        # Look up timezone and resolve date using default timezones
        return PyCalendar.sICalendar.getTimezoneOffsetSeconds(self.mTimezone, dt)

    def timeZoneDescriptor(self, dt):
        from manager import PyCalendarManager
        from calendar import PyCalendar
        if self.mUTC:
            return "(UTC)"
        elif not self.mTimezone:
            return PyCalendar.sICalendar.getTimezoneDescriptor(PyCalendarManager.sICalendarManager.getDefaultTimezone().getTimezoneID(), dt)

        # Look up timezone and resolve date using default timezones
        return PyCalendar.sICalendar.getTimezoneDescriptor(self.mTimezone, dt)

    def _copy_PyCalendarTimezone(self, copy):
        self.mUTC = copy.mUTC
        self.mTimezone = copy.mTimezone
    