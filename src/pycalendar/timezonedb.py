##
#    Copyright (c) 2011-2012 Cyrus Daboo. All rights reserved.
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

from pycalendar.exceptions import NoTimezoneInDatabase, \
    InvalidData
import os

class TimezoneDatabase(object):
    """
    On demand timezone database cache. This scans a TZdb directory for .ics files matching a
    TZID and caches the component data in a calendar from whence the actual component is returned.
    """

    sTimezoneDatabase = None


    @staticmethod
    def createTimezoneDatabase(dbpath):
        TimezoneDatabase.sTimezoneDatabase = TimezoneDatabase()
        TimezoneDatabase.sTimezoneDatabase.setPath(dbpath)


    @staticmethod
    def clearTimezoneDatabase():
        if TimezoneDatabase.sTimezoneDatabase is not None:
            TimezoneDatabase.sTimezoneDatabase.clear()


    def __init__(self):
        from pycalendar.icalendar.calendar import Calendar
        self.dbpath = None
        self.calendar = Calendar()


    def setPath(self, dbpath):
        self.dbpath = dbpath


    def clear(self):
        from pycalendar.icalendar.calendar import Calendar
        self.calendar = Calendar()


    @staticmethod
    def getTimezoneDatabase():
        if TimezoneDatabase.sTimezoneDatabase is None:
            TimezoneDatabase.sTimezoneDatabase = TimezoneDatabase()
        return TimezoneDatabase.sTimezoneDatabase


    @staticmethod
    def getTimezone(tzid):

        # Check whether current cached
        tzdb = TimezoneDatabase.getTimezoneDatabase()
        tz = tzdb.calendar.getTimezone(tzid)
        if tz is None:
            try:
                tzdb.cacheTimezone(tzid)
            except NoTimezoneInDatabase:
                pass
            tz = tzdb.calendar.getTimezone(tzid)

        return tz


    @staticmethod
    def getTimezoneInCalendar(tzid):
        """
        Return a VTIMEZONE inside a valid VCALENDAR
        """

        tz = TimezoneDatabase.getTimezone(tzid)
        if tz is not None:
            from pycalendar.icalendar.calendar import Calendar
            cal = Calendar()
            cal.addComponent(tz.duplicate(cal))
            return cal
        else:
            return None


    @staticmethod
    def getTimezoneOffsetSeconds(tzid, dt):
        # Cache it first
        tz = TimezoneDatabase.getTimezone(tzid)
        if tz is not None:
            return tz.getTimezoneOffsetSeconds(dt)
        else:
            return 0


    @staticmethod
    def getTimezoneDescriptor(tzid, dt):
        # Cache it first
        tz = TimezoneDatabase.getTimezone(tzid)
        if tz is not None:
            return tz.getTimezoneDescriptor(dt)
        else:
            return ""


    def cacheTimezone(self, tzid):

        if self.dbpath is None:
            return

        tzpath = os.path.join(self.dbpath, "%s.ics" % (tzid,))
        tzpath = os.path.normpath(tzpath)
        if tzpath.startswith(self.dbpath) and os.path.isfile(tzpath):
            try:
                self.calendar.parseComponent(open(tzpath))
            except (IOError, InvalidData):
                raise NoTimezoneInDatabase(self.dbpath, tzid)
        else:
            raise NoTimezoneInDatabase(self.dbpath, tzid)


    def addTimezone(self, tz):
        copy = tz.duplicate(self.calendar)
        self.calendar.addComponent(copy)


    @staticmethod
    def mergeTimezones(cal, tzs):
        """
        Merge each timezone from other calendar.
        """

        tzdb = TimezoneDatabase.getTimezoneDatabase()

        # Not if our own calendar
        if cal is tzdb.calendar:
            return

        # Merge each timezone from other calendar
        for tz in tzs:
            tzdb.mergeTimezone(tz)


    def mergeTimezone(self, tz):
        """
        If the supplied VTIMEZONE is not in our cache then store it in memory.
        """

        if self.getTimezone(tz.getID()) is None:
            self.addTimezone(tz)
