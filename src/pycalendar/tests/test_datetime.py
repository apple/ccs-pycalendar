##
#    Copyright (c) 2011-2013 Cyrus Daboo. All rights reserved.
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
from pycalendar.parser import ParserContext
from pycalendar.timezone import Timezone
import unittest

class TestDateTime(unittest.TestCase):

    def _patch(self, obj, attr, value):
        oldvalue = getattr(obj, attr)
        setattr(obj, attr, value)
        def _restore():
            setattr(obj, attr, oldvalue)
        self.addCleanup(_restore)


    def testDuplicateASUTC(self):

        items = (
            (
                DateTime(2011, 1, 1, 0, 0, 0, tzid=Timezone(utc=True)),
                DateTime(2011, 1, 1, 0, 0, 0, tzid=Timezone(utc=True)),
            ),
            (
                DateTime(2011, 1, 1, 0, 0, 0),
                DateTime(2011, 1, 1, 0, 0, 0),
            ),
            (
                DateTime(2011, 1, 1),
                DateTime(2011, 1, 1),
            )
        )

        for item, result in items:
            dup = item.duplicateAsUTC()
            self.assertEqual(str(dup), str(result), "Failed to convert '%s'" % (item,))


    def testDuplicateInSet(self):

        s = set(
            (
                DateTime(2011, 1, 1, 0, 0, 0, tzid=Timezone(utc=True)),
                DateTime(2011, 1, 2, 0, 0, 0, tzid=Timezone(utc=True)),
            )
        )

        self.assertTrue(DateTime(2011, 1, 1, 0, 0, 0, tzid=Timezone(utc=True)) in s)
        self.assertFalse(DateTime(2011, 1, 3, 0, 0, 0, tzid=Timezone(utc=True)) in s)


    def testRoundtrip(self):

        data1 = (
            "20110102",
            "20110103T121212",
            "20110103T121212Z",
            "00010102",
            "00010103T121212",
            "00010103T121212Z",
        )

        data2 = (
            ("20110102", "20110102"),
            ("2011-01-02", "20110102"),
            ("20110103T121212", "20110103T121212"),
            ("2011-01-03T12:12:12", "20110103T121212"),
            ("20110103T121212Z", "20110103T121212Z"),
            ("2011-01-03T12:12:12Z", "20110103T121212Z"),
            ("20110103T121212+0100", "20110103T121212+0100"),
            ("2011-01-03T12:12:12-0500", "20110103T121212-0500"),
            ("20110103T121212,123", "20110103T121212"),
            ("2011-01-03T12:12:12,123", "20110103T121212"),
            ("20110103T121212,123Z", "20110103T121212Z"),
            ("2011-01-03T12:12:12,123Z", "20110103T121212Z"),
            ("20110103T121212,123+0100", "20110103T121212+0100"),
            ("2011-01-03T12:12:12,123-0500", "20110103T121212-0500"),
        )

        for item in data1:
            dt = DateTime.parseText(item, False)
            self.assertEqual(dt.getText(), item, "Failed on: %s" % (item,))

        for item, result in data2:
            dt = DateTime.parseText(item, True)
            self.assertEqual(dt.getText(), result, "Failed on: %s" % (item,))


    def testBadParse(self):

        self._patch(ParserContext, "INVALID_DATETIME_LEADINGSPACE", ParserContext.PARSER_RAISE)

        data1 = (
            "2011",
            "201101023",
            "20110103t121212",
            "20110103T1212",
            "20110103T1212123",
            "20110103T121212A",
            "2011-01-03T121212Z",
            "20110103T12:12:12Z",
            "20110103T121212+0500",
            "   10102",
            "   10102T010101",
            "2011 102",
            "201101 3T121212",
            "-1110102",
            "2011-102",
            "201101-3T121212",
        )
        data2 = (
            "2011-01+02",
            "20110103T12-12-12",
            "2011-01-03T12:12:12,",
            "2011-01-03T12:12:12,ABC",
            "20110103T12:12:12-1",
        )

        for item in data1:
            self.assertRaises(ValueError, DateTime.parseText, item, False)

        for item in data2:
            self.assertRaises(ValueError, DateTime.parseText, item, False)


    def testBadParseFixed(self):

        self._patch(ParserContext, "INVALID_DATETIME_LEADINGSPACE", ParserContext.PARSER_ALLOW)

        data = (
            ("   10102", "00010102"),
            ("2001 102", "20010102"),
            ("200101 2", "20010102"),
            ("   10102T010101", "00010102T010101"),
            ("2001 102T010101", "20010102T010101"),
            ("200101 2T010101", "20010102T010101"),
        )

        for item, result in data:
            dt = DateTime.parseText(item)
            self.assertEqual(str(dt), result)


    def testCachePreserveOnAdjustment(self):

        # UTC first
        dt = DateTime(2012, 6, 7, 12, 0, 0, Timezone(tzid="utc"))
        dt.getPosixTime()

        # check existing cache is complete
        self.assertTrue(dt.mPosixTimeCached)
        self.assertNotEqual(dt.mPosixTime, 0)
        self.assertEqual(dt.mTZOffset, None)

        # duplicate preserves cache details
        dt2 = dt.duplicate()
        self.assertTrue(dt2.mPosixTimeCached)
        self.assertEqual(dt2.mPosixTime, dt.mPosixTime)
        self.assertEqual(dt2.mTZOffset, dt.mTZOffset)

        # adjust preserves cache details
        dt2.adjustToUTC()
        self.assertTrue(dt2.mPosixTimeCached)
        self.assertEqual(dt2.mPosixTime, dt.mPosixTime)
        self.assertEqual(dt2.mTZOffset, dt.mTZOffset)

        # Now timezone
        tzdata = """BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//calendarserver.org//Zonal//EN
VERSION:2.0
BEGIN:VTIMEZONE
TZID:America/Pittsburgh
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
""".replace("\n", "\r\n")

        Calendar.parseText(tzdata)

        dt = DateTime(2012, 6, 7, 12, 0, 0, Timezone(tzid="America/Pittsburgh"))
        dt.getPosixTime()

        # check existing cache is complete
        self.assertTrue(dt.mPosixTimeCached)
        self.assertNotEqual(dt.mPosixTime, 0)
        self.assertEqual(dt.mTZOffset, -14400)

        # duplicate preserves cache details
        dt2 = dt.duplicate()
        self.assertTrue(dt2.mPosixTimeCached)
        self.assertEqual(dt2.mPosixTime, dt.mPosixTime)
        self.assertEqual(dt2.mTZOffset, dt.mTZOffset)

        # adjust preserves cache details
        dt2.adjustToUTC()
        self.assertTrue(dt2.mPosixTimeCached)
        self.assertEqual(dt2.mPosixTime, dt.mPosixTime)
        self.assertEqual(dt2.mTZOffset, 0)


    def testSetWeekNo(self):

        dt = DateTime(2013, 1, 1, 0, 0, 0, tzid=Timezone(utc=True))
        self.assertEqual(dt.getWeekNo(), 1)
        dt.setWeekNo(1)
        self.assertEqual(dt, DateTime(2013, 1, 1, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 1)

        dt = DateTime(2013, 1, 1, 0, 0, 0, tzid=Timezone(utc=True))
        self.assertEqual(dt.getWeekNo(), 1)
        dt.setWeekNo(2)
        self.assertEqual(dt, DateTime(2013, 1, 8, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 2)

        dt = DateTime(2013, 1, 8, 0, 0, 0, tzid=Timezone(utc=True))
        self.assertEqual(dt.getWeekNo(), 2)
        dt.setWeekNo(1)
        self.assertEqual(dt, DateTime(2013, 1, 1, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 1)

        dt = DateTime(2014, 1, 7, 0, 0, 0, tzid=Timezone(utc=True))
        self.assertEqual(dt.getWeekNo(), 2)
        dt.setWeekNo(1)
        self.assertEqual(dt, DateTime(2013, 12, 31, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 1)

        dt = DateTime(2012, 12, 31, 0, 0, 0, tzid=Timezone(utc=True))
        self.assertEqual(dt.getWeekNo(), 1)
        dt.setWeekNo(1)
        self.assertEqual(dt, DateTime(2012, 12, 31, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 1)

        dt = DateTime(2016, 1, 1, 0, 0, 0, tzid=Timezone(utc=True))
        self.assertEqual(dt.getWeekNo(), 53)
        dt.setWeekNo(1)
        self.assertEqual(dt, DateTime(2016, 1, 8, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 1)
        dt.setWeekNo(2)
        self.assertEqual(dt, DateTime(2016, 1, 15, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 2)

        dt = DateTime(2016, 1, 8, 0, 0, 0, tzid=Timezone(utc=True))
        self.assertEqual(dt.getWeekNo(), 1)
        dt.setWeekNo(1)
        self.assertEqual(dt, DateTime(2016, 1, 8, 0, 0, 0, tzid=Timezone(utc=True)))
        self.assertEqual(dt.getWeekNo(), 1)
