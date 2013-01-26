# coding: utf-8
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

from pycalendar.attribute import PyCalendarAttribute
from pycalendar.calendar import PyCalendar
import cStringIO as StringIO
import unittest

class TestCalendar(unittest.TestCase):

    def testAddCN(self):

        data = (
"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
ORGANIZER:user01@example.com
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

    "まだ",

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
ORGANIZER;CN=まだ:user01@example.com
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

        )

        cal1 = PyCalendar()
        cal1.parse(StringIO.StringIO(data[0]))

        vevent = cal1.getComponents("VEVENT")[0]
        organizer = vevent.getProperties("ORGANIZER")[0]
        organizer.addAttribute(PyCalendarAttribute("CN", data[1]))

        cal2 = PyCalendar()
        cal2.parse(StringIO.StringIO(data[2]))

        self.assertEqual(str(cal1), str(cal2))
