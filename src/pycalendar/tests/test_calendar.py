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

from pycalendar.calendar import PyCalendar
from pycalendar.datetime import PyCalendarDateTime
from pycalendar.exceptions import PyCalendarInvalidData
from pycalendar.parser import ParserContext
from pycalendar.period import PyCalendarPeriod
from pycalendar.property import PyCalendarProperty
import cStringIO as StringIO
import difflib
import unittest

class TestCalendar(unittest.TestCase):
    
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
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
X-WR-CALNAME:PayDay
BEGIN:VTIMEZONE
TZID:US/Eastern
LAST-MODIFIED:20040110T032845Z
BEGIN:DAYLIGHT
DTSTART:20000404T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20001026T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
UID:DC3D0301C7790B38631F1FBB@ninevah.local
DTSTART;VALUE=DATE:20040227
DTSTAMP:20050211T173501Z
RRULE:FREQ=MONTHLY;BYDAY=-1MO,-1TU,-1WE,-1TH,-1FR;BYSETPOS=-1
SUMMARY:PAY DAY
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Alarm for Organizer!
TRIGGER;RELATED=START:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:12345-67890-3
DTSTART:20071114T000000Z
ATTENDEE:mailto:user2@example.com
EXDATE:20081114T000000Z
ORGANIZER:mailto:user1@example.com
RRULE:FREQ=YEARLY
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
ATTACH:http://example.com/test.jpg
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
ATTACH;ENCODING=BASE64;VALUE=BINARY:dGVzdA==
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Example Inc.//Example Calendar//EN
BEGIN:VTIMEZONE
TZID:America/Montreal
LAST-MODIFIED:20040110T032845Z
BEGIN:DAYLIGHT
DTSTART:20000404T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20001026T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
BEGIN:VAVAILABILITY
UID:20061005T133225Z-00001-availability@example.com
DTSTART;TZID=America/Montreal:20060101T000000
DTEND;TZID=America/Montreal:20060108T000000
DTSTAMP:20061005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20061005T133225Z-00001-A-availability@example.com
DTSTART;TZID=America/Montreal:20060102T090000
DTEND;TZID=America/Montreal:20060102T120000
DTSTAMP:20061005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR
SUMMARY:Monday\\, Wednesday and Friday from 9:00 to 12:00
END:AVAILABLE
BEGIN:AVAILABLE
UID:20061005T133225Z-00001-A-availability@example.com
RECURRENCE-ID;TZID=America/Montreal:20060106T090000
DTSTART;TZID=America/Montreal:20060106T120000
DTEND;TZID=America/Montreal:20060106T170000
DTSTAMP:20061005T133225Z
SUMMARY:Friday override from 12:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Example Inc.//Example Calendar//EN
BEGIN:VTODO
UID:event1@ninevah.local
CREATED:20060101T150000Z
DTSTAMP:20051222T205953Z
SUMMARY:event 1
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),

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
SUMMARY:New Year's Day
END:VEVENT
BEGIN:X-COMPONENT
UID:1234
END:X-COMPONENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Apple Inc.//iCal 4.0.1//EN
BEGIN:VTIMEZONE
TZID:US/Pacific
BEGIN:DAYLIGHT
DTSTART:20070311T020000
RRULE:FREQ=YEARLY;BYDAY=2SU;BYMONTH=3
TZNAME:PDT
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20071104T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=11
TZNAME:PST
TZOFFSETFROM:-0700
TZOFFSETTO:-0800
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
UID:uid4
DTSTART;TZID=US/Pacific:20100207T170000
DTEND;TZID=US/Pacific:20100207T173000
CREATED:20100203T013849Z
DTSTAMP:20100203T013909Z
SEQUENCE:3
SUMMARY:New Event
TRANSP:OPAQUE
BEGIN:VALARM
ACTION:AUDIO
ATTACH:Basso
TRIGGER:-PT20M
X-WR-ALARMUID:1377CCC7-F85C-4610-8583-9513D4B364E1
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
ATTACH:http://example.com/test.jpg
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
X-APPLE-STRUCTURED-LOCATION:geo:123.123,123.123
X-Test:Some\, text.
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
ATTACH:http://example.com/test.jpg
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
X-APPLE-STRUCTURED-LOCATION;VALUE=URI:geo:123.123,123.123
X-Test:Some\, text.
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

)
    data2 = (
                (
"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:12345-67890-3
DTSTART:20071114T000000Z
ATTENDEE:mailto:user2@example.com
EXDATE:20081114T000000Z
ORGANIZER:mailto:user1@example.com
RRULE:FREQ=YEARLY
END:VEVENT
X-TEST:Testing
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
X-TEST:Testing
BEGIN:VEVENT
UID:12345-67890-3
DTSTART:20071114T000000Z
ATTENDEE:mailto:user2@example.com
EXDATE:20081114T000000Z
ORGANIZER:mailto:user1@example.com
RRULE:FREQ=YEARLY
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                ),
)

    def testRoundtrip(self):

        def _doRoundtrip(caldata, resultdata=None):
            test1 = resultdata if resultdata is not None else caldata

            cal = PyCalendar()
            cal.parse(StringIO.StringIO(caldata))
            
            s = StringIO.StringIO()
            cal.generate(s)
            test2 = s.getvalue()
            
            self.assertEqual(
                test1,
                test2,
                "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
            )

        for item in self.data:
            _doRoundtrip(item)

        for item1, item2 in self.data2:
            _doRoundtrip(item1, item2)

    def testRoundtripDuplicate(self):

        def _doDuplicateRoundtrip(caldata):
            cal = PyCalendar()
            cal.parse(StringIO.StringIO(caldata))
            cal = cal.duplicate()
            
            s = StringIO.StringIO()
            cal.generate(s)
            self.assertEqual(caldata, s.getvalue())

        for item in self.data:
            _doDuplicateRoundtrip(item)

    def testEquality(self):

        def _doEquality(caldata):
            cal1 = PyCalendar()
            cal1.parse(StringIO.StringIO(caldata))

            cal2 = PyCalendar()
            cal2.parse(StringIO.StringIO(caldata))

            self.assertEqual(cal1, cal2, "%s\n\n%s" % (cal1, cal2,))

        def _doNonEquality(caldata):
            cal1 = PyCalendar()
            cal1.parse(StringIO.StringIO(caldata))

            cal2 = PyCalendar()
            cal2.parse(StringIO.StringIO(caldata))
            cal2.addProperty(PyCalendarProperty("X-FOO", "BAR"))

            self.assertNotEqual(cal1, cal2)

        for item in self.data:
            _doEquality(item)
            _doNonEquality(item)

    def testParseComponent(self):
        
        data1 = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")

        data2 = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//Example Inc.//Example Calendar//EN
BEGIN:VTIMEZONE
TZID:America/Montreal
LAST-MODIFIED:20040110T032845Z
BEGIN:DAYLIGHT
DTSTART:20000404T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20001026T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
""".replace("\n", "\r\n")


        result = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTIMEZONE
TZID:America/Montreal
LAST-MODIFIED:20040110T032845Z
BEGIN:DAYLIGHT
DTSTART:20000404T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20001026T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")


        cal = PyCalendar()
        cal.parse(StringIO.StringIO(data1))
        cal.parseComponent(StringIO.StringIO(data2))
        self.assertEqual(str(cal), result)

    def testParseFail(self):
        
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
SUMMARY:New Year's Day
END:VEVENT
""".replace("\n", "\r\n"),

"""BEGIN:VCARD
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
VERSION:2.0
END:VCARD
""".replace("\n", "\r\n"),

"""BOGUS
BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BOGUS

BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

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
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
BOGUS
""".replace("\n", "\r\n"),

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
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR

BOGUS
""".replace("\n", "\r\n"),

        )

        for item in data:
            self.assertRaises(PyCalendarInvalidData, PyCalendar.parseText, item)

    def testParseBlank(self):
        
        data = (
"""
BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""

BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

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
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR


""".replace("\n", "\r\n"),

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
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

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
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
        )

        save = ParserContext.BLANK_LINES_IN_DATA
        for item in data:
            ParserContext.BLANK_LINES_IN_DATA = ParserContext.PARSER_RAISE
            self.assertRaises(PyCalendarInvalidData, PyCalendar.parseText, item)

            ParserContext.BLANK_LINES_IN_DATA = ParserContext.PARSER_IGNORE
            lines = item.split("\r\n")
            result = "\r\n".join([line for line in lines if line]) + "\r\n"
            self.assertEqual(str(PyCalendar.parseText(item)), result)

        ParserContext.BLANK_LINES_IN_DATA = save

    def testGetVEvents(self):

        data = (
            (
                "Non-recurring match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20110601
DURATION:P1D
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (PyCalendarDateTime(2011, 6, 1),),
            ),
            (
                "Non-recurring no-match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20110501
DURATION:P1D
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (),
            ),
            (
                "Recurring match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20110601
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=DAILY;COUNT=2
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (
                    PyCalendarDateTime(2011, 6, 1),
                    PyCalendarDateTime(2011, 6, 2),
                ),
            ),
            (
                "Recurring no match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20110501
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=DAILY;COUNT=2
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (),
            ),
            (
                "Recurring with override match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART:20110601T120000
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=DAILY;COUNT=2
SUMMARY:New Year's Day
END:VEVENT
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
RECURRENCE-ID;VALUE=DATE:20110602T120000
DTSTART;VALUE=DATE:20110602T130000
DURATION:P1D
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (
                    PyCalendarDateTime(2011, 6, 1, 12, 0, 0),
                    PyCalendarDateTime(2011, 6, 2, 13, 0, 0),
                ),
            ),
            (
                "Recurring with override no match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART:20110501T120000
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=DAILY;COUNT=2
SUMMARY:New Year's Day
END:VEVENT
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
RECURRENCE-ID;VALUE=DATE:20110502T120000
DTSTART;VALUE=DATE:20110502T130000
DURATION:P1D
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (),
            ),
            (
                "Recurring partial match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20110531
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=DAILY;COUNT=2
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (
                    PyCalendarDateTime(2011, 6, 1),
                ),
            ),
            (
                "Recurring with override partial match",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART:20110531T120000
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=DAILY;COUNT=2
SUMMARY:New Year's Day
END:VEVENT
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
RECURRENCE-ID;VALUE=DATE:20110601T120000
DTSTART;VALUE=DATE:20110601T130000
DURATION:P1D
DTSTAMP:20020101T000000Z
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                (
                    PyCalendarDateTime(2011, 6, 1, 13, 0, 0),
                ),
            ),
        )

        for title, caldata, result in data: 
            calendar = PyCalendar.parseText(caldata)
            instances = []
            calendar.getVEvents(
                PyCalendarPeriod(
                    start=PyCalendarDateTime(2011, 6, 1),
                    end=PyCalendarDateTime(2011, 7, 1),
                ),
                instances
            )
            instances = tuple([instance.getInstanceStart() for instance in instances])
            self.assertEqual(instances, result, "Failed in %s: got %s, expected %s" % (title, instances, result))
