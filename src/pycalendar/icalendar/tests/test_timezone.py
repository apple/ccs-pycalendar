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

from pycalendar.datetime import DateTime
from pycalendar.icalendar.calendar import Calendar
import unittest

class TestCalendar(unittest.TestCase):

    def testOffsets(self):

        data = (
                    ("""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//calendarserver.org//Zonal//EN
VERSION:2.0
BEGIN:VTIMEZONE
TZID:America/New_York
X-LIC-LOCATION:America/New_York
BEGIN:STANDARD
DTSTART:18831118T120358
RDATE:18831118T120358
TZNAME:EST
TZOFFSETFROM:-045602
TZOFFSETTO:-0500
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19180331T020000
RRULE:FREQ=YEARLY;UNTIL=19190330T070000Z;BYDAY=-1SU;BYMONTH=3
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19181027T020000
RRULE:FREQ=YEARLY;UNTIL=19191026T060000Z;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
BEGIN:STANDARD
DTSTART:19200101T000000
RDATE:19200101T000000
RDATE:19420101T000000
RDATE:19460101T000000
RDATE:19670101T000000
TZNAME:EST
TZOFFSETFROM:-0500
TZOFFSETTO:-0500
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19200328T020000
RDATE:19200328T020000
RDATE:19740106T020000
RDATE:19750223T020000
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19201031T020000
RDATE:19201031T020000
RDATE:19450930T020000
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19210424T020000
RRULE:FREQ=YEARLY;UNTIL=19410427T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19210925T020000
RRULE:FREQ=YEARLY;UNTIL=19410928T060000Z;BYDAY=-1SU;BYMONTH=9
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19420209T020000
RDATE:19420209T020000
TZNAME:EWT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:DAYLIGHT
DTSTART:19450814T190000
RDATE:19450814T190000
TZNAME:EPT
TZOFFSETFROM:-0400
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:DAYLIGHT
DTSTART:19460428T020000
RRULE:FREQ=YEARLY;UNTIL=19660424T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19460929T020000
RRULE:FREQ=YEARLY;UNTIL=19540926T060000Z;BYDAY=-1SU;BYMONTH=9
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
BEGIN:STANDARD
DTSTART:19551030T020000
RRULE:FREQ=YEARLY;UNTIL=19661030T060000Z;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19670430T020000
RRULE:FREQ=YEARLY;UNTIL=19730429T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;UNTIL=20061029T060000Z;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19760425T020000
RRULE:FREQ=YEARLY;UNTIL=19860427T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:DAYLIGHT
DTSTART:19870405T020000
RRULE:FREQ=YEARLY;UNTIL=20060402T070000Z;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:DAYLIGHT
DTSTART:20070311T020000
RRULE:FREQ=YEARLY;BYDAY=2SU;BYMONTH=3
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20071104T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=11
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
""",
                (
                    (DateTime(1942, 2, 8), -5),
                    (DateTime(1942, 2, 10), -4),
                    (DateTime(2011, 1, 1), -5),
                    (DateTime(2011, 4, 1), -4),
                    (DateTime(2011, 10, 24), -4),
                    (DateTime(2011, 11, 8), -5),
                    (DateTime(2006, 1, 1), -5),
                    (DateTime(2006, 4, 1), -5),
                    (DateTime(2006, 5, 1), -4),
                    (DateTime(2006, 10, 1), -4),
                    (DateTime(2006, 10, 24), -4),
                    (DateTime(2006, 11, 8), -5),
                )
            ),
                    ("""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//calendarserver.org//Zonal//EN
VERSION:2.0
BEGIN:VTIMEZONE
TZID:Etc/GMT+8
X-LIC-LOCATION:Etc/GMT+8
BEGIN:STANDARD
DTSTART:18000101T000000
RDATE:18000101T000000
TZNAME:GMT+8
TZOFFSETFROM:-0800
TZOFFSETTO:-0800
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
""",
                (
                    (DateTime(1942, 2, 8), -8),
                    (DateTime(1942, 2, 10), -8),
                    (DateTime(2011, 1, 1), -8),
                    (DateTime(2011, 4, 1), -8),
                )
            ),
        )

        for tzdata, offsets in data:

            cal = Calendar.parseText(tzdata.replace("\n", "\r\n"))
            tz = cal.getComponents()[0]

            for dt, offset in offsets:
                tzoffset = tz.getTimezoneOffsetSeconds(dt)
                self.assertEqual(tzoffset, offset * 60 * 60, "Failed to match offset for %s at %s with caching" % (tz.getID(), dt,))
            for dt, offset in reversed(offsets):
                tzoffset = tz.getTimezoneOffsetSeconds(dt)
                self.assertEqual(tzoffset, offset * 60 * 60, "Failed to match offset for %s at %s with caching, reversed" % (tz.getID(), dt,))

            for dt, offset in offsets:
                tz.mCachedExpandAllMax = None
                tzoffset = tz.getTimezoneOffsetSeconds(dt)
                self.assertEqual(tzoffset, offset * 60 * 60, "Failed to match offset for %s at %s without caching" % (tz.getID(), dt,))
            for dt, offset in reversed(offsets):
                tz.mCachedExpandAllMax = None
                tzoffset = tz.getTimezoneOffsetSeconds(dt)
                self.assertEqual(tzoffset, offset * 60 * 60, "Failed to match offset for %s at %s without caching, reversed" % (tz.getID(), dt,))
