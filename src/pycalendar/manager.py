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

from pycalendar.timezone import Timezone

class CalendarManager(object):

    sICalendarManager = None

    def __init__(self):
        Timezone.sDefaultTimezone = Timezone()


    def initManager(self):
        # TODO: - read in timezones from vtimezones.ics file

        # Eventually we need to read these from prefs - for now they are
        # hard-coded to my personal prefs!
        self.setDefaultTimezone(Timezone(utc=False, tzid="US/Eastern"))


    def setDefaultTimezoneID(self, tzid):
        # Check for UTC
        if tzid == "UTC":
            temp = Timezone(utc=True)
            self.setDefaultTimezone(temp)
        else:
            temp = Timezone(utc=False, tzid=tzid)
            self.setDefaultTimezone(temp)


    def setDefaultTimezone(self, tzid):
        Timezone.sDefaultTimezone = tzid


    def getDefaultTimezoneID(self):
        if Timezone.sDefaultTimezone.getUTC():
            return "UTC"
        else:
            return Timezone.sDefaultTimezone.getTimezoneID()


    def getDefaultTimezone(self):
        return Timezone.sDefaultTimezone

CalendarManager.sICalendarManager = CalendarManager()
