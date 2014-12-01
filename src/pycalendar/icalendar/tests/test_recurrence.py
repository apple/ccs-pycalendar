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
from pycalendar.period import Period
from pycalendar.icalendar.recurrence import Recurrence
import unittest
from pycalendar.timezone import Timezone

class TestRecurrence(unittest.TestCase):

    items = (
        "FREQ=DAILY",
        "FREQ=YEARLY;COUNT=400",
        "FREQ=MONTHLY;UNTIL=20110102",
        "FREQ=MONTHLY;UNTIL=20110102T090000",
        "FREQ=MONTHLY;UNTIL=20110102T100000Z",
        "FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,TH;BYSETPOS=-1",

        # These are from RFC5545 examples
        "FREQ=YEARLY;INTERVAL=2;BYMINUTE=30;BYHOUR=8,9;BYDAY=SU;BYMONTH=1",
        "FREQ=YEARLY;UNTIL=19730429T070000Z;BYDAY=-1SU;BYMONTH=4",
        "FREQ=YEARLY;UNTIL=20060402T070000Z;BYDAY=1SU;BYMONTH=4",
        "FREQ=YEARLY;BYDAY=2SU;BYMONTH=3",
        "FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10",
        "FREQ=DAILY;INTERVAL=2",
        "FREQ=DAILY;COUNT=5;INTERVAL=10",
        "FREQ=DAILY;UNTIL=20000131T140000Z;BYMONTH=1",
        "FREQ=WEEKLY;INTERVAL=2;WKST=SU",
        "FREQ=WEEKLY;UNTIL=19971007T000000Z;BYDAY=TU,TH;WKST=SU",
        "FREQ=WEEKLY;COUNT=10;BYDAY=TU,TH;WKST=SU",
        "FREQ=WEEKLY;UNTIL=19971224T000000Z;INTERVAL=2;BYDAY=MO,WE,FR;WKST=SU",
        "FREQ=WEEKLY;COUNT=8;INTERVAL=2;BYDAY=TU,TH;WKST=SU",
        "FREQ=MONTHLY;BYMONTHDAY=-3",
        "FREQ=MONTHLY;COUNT=10;BYMONTHDAY=1,-1",
        "FREQ=MONTHLY;COUNT=10;INTERVAL=18;BYMONTHDAY=10,11,12,13,14,15",
        "FREQ=YEARLY;COUNT=10;INTERVAL=3;BYYEARDAY=1,100,200",
        "FREQ=YEARLY;BYDAY=MO;BYWEEKNO=20",
        "FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,TH;BYSETPOS=3",
        "FREQ=DAILY;BYMINUTE=0,20,40;BYHOUR=9,10,11,12,13,14,15,16",

        # RSCALE
        "RSCALE=CHINESE;FREQ=DAILY",
        "RSCALE=GREGORIAN;FREQ=YEARLY;COUNT=400;SKIP=YES",
        "RSCALE=GREGORIAN;FREQ=YEARLY;COUNT=400;SKIP=BACKWARD",
        "RSCALE=GREGORIAN;FREQ=YEARLY;COUNT=400;SKIP=FORWARD",
        "RSCALE=CHINESE;FREQ=YEARLY;BYMONTH=5,6,6L,7",

    )


    def testParse(self):

        for item in TestRecurrence.items:
            recur = Recurrence()
            recur.parse(item)
            self.assertEqual(recur.getText(), item, "Failed to parse and re-generate '%s' '%s'" % (item, recur.getText()))


    def testParseInvalid(self):

        items = (
            "",
            "FREQ=",
            "FREQ=MICROSECONDLY",
            "FREQ=YEARLY;COUNT=ABC",
            "FREQ=YEARLY;COUNT=123;UNTIL=20110102",
            "FREQ=MONTHLY;UNTIL=20110102T",
            "FREQ=MONTHLY;UNTIL=20110102t090000",
            "FREQ=MONTHLY;UNTIL=20110102T100000z",
            "FREQ=MONTHLY;UNTIL=20110102TAABBCCz",
            "FREQ=MONTHLY;BYDAY=A",
            "FREQ=MONTHLY;BYDAY=+1,3MO",
            "FREQ=MONTHLY;BYHOUR=A",
            "FREQ=MONTHLY;BYHOUR=54",
            "FREQ=MONTHLY;SKIP=YES",
            "RSCALE=CHINESE;FREQ=MONTHLY;SKIP=NO",
        )

        for item in items:
            self.assertRaises(ValueError, Recurrence().parse, item)


    def testEquality(self):

        recur1 = Recurrence()
        recur1.parse("FREQ=YEARLY;COUNT=400")
        recur2 = Recurrence()
        recur2.parse("COUNT=400;FREQ=YEARLY")

        self.assertEqual(recur1, recur2)


    def testInequality(self):

        recur1 = Recurrence()
        recur1.parse("FREQ=YEARLY;COUNT=400")
        recur2 = Recurrence()
        recur2.parse("COUNT=400;FREQ=YEARLY;BYMONTH=1")

        self.assertNotEqual(recur1, recur2)


    def testHash(self):

        hashes = []
        for item in TestRecurrence.items:
            recur = Recurrence()
            recur.parse(item)
            hashes.append(hash(recur))
        hashes.sort()
        for i in range(1, len(hashes)):
            self.assertNotEqual(hashes[i - 1], hashes[i])


    def testByWeekNoExpand(self):

        rule = "FREQ=YEARLY;BYWEEKNO=1,2"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2013, 1, 1, 0, 0, 0)
            end = DateTime(2017, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2013, 1, 1, 0, 0, 0),
                    DateTime(2013, 1, 8, 0, 0, 0),
                    DateTime(2014, 1, 1, 0, 0, 0),
                    DateTime(2014, 1, 8, 0, 0, 0),
                    DateTime(2015, 1, 1, 0, 0, 0),
                    DateTime(2015, 1, 8, 0, 0, 0),
                    DateTime(2016, 1, 8, 0, 0, 0),
                    DateTime(2016, 1, 15, 0, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testMonthlyInvalidStart(self):

        rule = "FREQ=MONTHLY"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 40, 12, 0, 0)
            end = DateTime(2015, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 2, 9, 12, 0, 0),
                    DateTime(2014, 3, 9, 12, 0, 0),
                    DateTime(2014, 4, 9, 12, 0, 0),
                    DateTime(2014, 5, 9, 12, 0, 0),
                    DateTime(2014, 6, 9, 12, 0, 0),
                    DateTime(2014, 7, 9, 12, 0, 0),
                    DateTime(2014, 8, 9, 12, 0, 0),
                    DateTime(2014, 9, 9, 12, 0, 0),
                    DateTime(2014, 10, 9, 12, 0, 0),
                    DateTime(2014, 11, 9, 12, 0, 0),
                    DateTime(2014, 12, 9, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testWeeklyTwice(self):

        rule = "FREQ=WEEKLY"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(utc=True))
            end = DateTime(2014, 2, 1, 0, 0, 0, tzid=Timezone(utc=True))
            items = []
            range = Period(start, end)
            recur.expand(DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")), range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 8, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 15, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 22, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 29, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),

                ],
                msg="Failed: {}".format(rrule),
            )

            start = DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(utc=True))
            end = DateTime(2014, 3, 1, 0, 0, 0, tzid=Timezone(utc=True))
            items = []
            range = Period(start, end)
            recur.expand(DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")), range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 8, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 15, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 22, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 1, 29, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 2, 5, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 2, 12, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 2, 19, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 2, 26, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testMonthlyInUTC(self):

        rule = "FREQ=MONTHLY"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(utc=True))
            end = DateTime(2015, 1, 1, 0, 0, 0, tzid=Timezone(utc=True))
            items = []
            range = Period(start, end)
            recur.expand(DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")), range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 2, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 3, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 4, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 5, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 6, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 7, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 8, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 9, 1, 12, 0, 0, tzid=Timezone(tzid="America/New_York")),
                    DateTime(2014, 10, 1, 12, 0, 0),
                    DateTime(2014, 11, 1, 12, 0, 0),
                    DateTime(2014, 12, 1, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testMonthlyStart31st(self):

        rule = "FREQ=MONTHLY"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 31, 12, 0, 0)
            end = DateTime(2015, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 31, 12, 0, 0),
                    DateTime(2014, 3, 31, 12, 0, 0),
                    DateTime(2014, 5, 31, 12, 0, 0),
                    DateTime(2014, 7, 31, 12, 0, 0),
                    DateTime(2014, 8, 31, 12, 0, 0),
                    DateTime(2014, 10, 31, 12, 0, 0),
                    DateTime(2014, 12, 31, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testMonthlyByMonthDay31(self):

        rule = "FREQ=MONTHLY;BYMONTHDAY=31"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 31, 12, 0, 0)
            end = DateTime(2015, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 31, 12, 0, 0),
                    DateTime(2014, 3, 31, 12, 0, 0),
                    DateTime(2014, 5, 31, 12, 0, 0),
                    DateTime(2014, 7, 31, 12, 0, 0),
                    DateTime(2014, 8, 31, 12, 0, 0),
                    DateTime(2014, 10, 31, 12, 0, 0),
                    DateTime(2014, 12, 31, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testMonthlyByMonthDayMinus31(self):

        rule = "FREQ=MONTHLY;BYMONTHDAY=-31"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 1, 12, 0, 0)
            end = DateTime(2015, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 1, 12, 0, 0),
                    DateTime(2014, 3, 1, 12, 0, 0),
                    DateTime(2014, 5, 1, 12, 0, 0),
                    DateTime(2014, 7, 1, 12, 0, 0),
                    DateTime(2014, 8, 1, 12, 0, 0),
                    DateTime(2014, 10, 1, 12, 0, 0),
                    DateTime(2014, 12, 1, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testMonthlyByLastFridayExpand(self):

        rule = "FREQ=MONTHLY;BYDAY=-1FR"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 31, 12, 0, 0)
            end = DateTime(2015, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 31, 12, 0, 0),
                    DateTime(2014, 2, 28, 12, 0, 0),
                    DateTime(2014, 3, 28, 12, 0, 0),
                    DateTime(2014, 4, 25, 12, 0, 0),
                    DateTime(2014, 5, 30, 12, 0, 0),
                    DateTime(2014, 6, 27, 12, 0, 0),
                    DateTime(2014, 7, 25, 12, 0, 0),
                    DateTime(2014, 8, 29, 12, 0, 0),
                    DateTime(2014, 9, 26, 12, 0, 0),
                    DateTime(2014, 10, 31, 12, 0, 0),
                    DateTime(2014, 11, 28, 12, 0, 0),
                    DateTime(2014, 12, 26, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testMonthlyByFifthFridayExpand(self):

        rule = "FREQ=MONTHLY;BYDAY=5FR"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 31, 12, 0, 0)
            end = DateTime(2015, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 31, 12, 0, 0),
                    DateTime(2014, 5, 30, 12, 0, 0),
                    DateTime(2014, 8, 29, 12, 0, 0),
                    DateTime(2014, 10, 31, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testYearlyLeapDay(self):

        rule = "FREQ=YEARLY"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2012, 2, 29, 12, 0, 0)
            end = DateTime(2020, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2012, 2, 29, 12, 0, 0),
                    DateTime(2016, 2, 29, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testYearlyYearDay(self):

        rule = "FREQ=YEARLY;BYYEARDAY=366"
        for rrule in (
            rule,
            "RSCALE=GREGORIAN;{};SKIP=YES".format(rule)
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2012, 12, 31, 12, 0, 0)
            end = DateTime(2020, 1, 1, 0, 0, 0)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2012, 12, 31, 12, 0, 0),
                    DateTime(2016, 12, 31, 12, 0, 0),
                ],
                msg="Failed: {}".format(rrule),
            )


    def testClearOnChange(self):

        recur = Recurrence()
        recur.parse("FREQ=DAILY")

        start = DateTime(2013, 1, 1, 0, 0, 0)
        end = DateTime(2017, 1, 1, 0, 0, 0)
        range = Period(start, end)
        items = []
        recur.expand(start, range, items)
        self.assertTrue(recur.mCached)
        self.assertTrue(len(items) > 100)

        recur.setUseCount(True)
        recur.setCount(10)
        self.assertFalse(recur.mCached)
        items = []
        recur.expand(start, range, items)
        self.assertEqual(len(items), 10)



class TestRecurrenceRscale(unittest.TestCase):

    def testMonthlyRscaleStartInLeapYearSkipYes(self):

        recur = Recurrence()
        recur.parse("RSCALE=CHINESE;FREQ=MONTHLY;SKIP=YES")
        start = DateTime(2014, 1, 30) # {C}46501230
        end = DateTime(2018, 1, 1)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 1, 30),
                DateTime(2014, 3, 30),
                DateTime(2014, 5, 28),
                DateTime(2014, 7, 26),
                DateTime(2014, 9, 23),
                DateTime(2014, 10, 23),
                DateTime(2014, 12, 21),
                DateTime(2015, 2, 18),
                DateTime(2015, 4, 18),
                DateTime(2015, 7, 15),
                DateTime(2015, 9, 12),
                DateTime(2015, 10, 12),
                DateTime(2015, 11, 11),
                DateTime(2016, 1, 9),
                DateTime(2016, 3, 8),
                DateTime(2016, 5, 6),
                DateTime(2016, 8, 2),
                DateTime(2016, 9, 30),
                DateTime(2016, 10, 30),
                DateTime(2016, 12, 28),
                DateTime(2017, 1, 27),
                DateTime(2017, 3, 27),
                DateTime(2017, 5, 25),
                DateTime(2017, 8, 21),
                DateTime(2017, 10, 19),
                DateTime(2017, 12, 17),
            ],
        )


    def testMonthlyRscaleStartInLeapYearSkipForward(self):

        recur = Recurrence()
        recur.parse("RSCALE=CHINESE;FREQ=MONTHLY;SKIP=FORWARD")
        start = DateTime(2014, 1, 30) # {C}46501230
        end = DateTime(2018, 1, 1)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 1, 30),
                DateTime(2014, 3, 1),
                DateTime(2014, 3, 30),
                DateTime(2014, 4, 29),
                DateTime(2014, 5, 28),
                DateTime(2014, 6, 27),
                DateTime(2014, 7, 26),
                DateTime(2014, 8, 25),
                DateTime(2014, 9, 23),
                DateTime(2014, 10, 23),
                DateTime(2014, 11, 22),
                DateTime(2014, 12, 21),
                DateTime(2015, 1, 20),
                DateTime(2015, 2, 18),
                DateTime(2015, 3, 20),
                DateTime(2015, 4, 18),
                DateTime(2015, 5, 18),
                DateTime(2015, 6, 16),
                DateTime(2015, 7, 15),
                DateTime(2015, 8, 14),
                DateTime(2015, 9, 12),
                DateTime(2015, 10, 12),
                DateTime(2015, 11, 11),
                DateTime(2015, 12, 11),
                DateTime(2016, 1, 9),
                DateTime(2016, 2, 8),
                DateTime(2016, 3, 8),
                DateTime(2016, 4, 7),
                DateTime(2016, 5, 6),
                DateTime(2016, 6, 5),
                DateTime(2016, 7, 4),
                DateTime(2016, 8, 2),
                DateTime(2016, 9, 1),
                DateTime(2016, 9, 30),
                DateTime(2016, 10, 30),
                DateTime(2016, 11, 29),
                DateTime(2016, 12, 28),
                DateTime(2017, 1, 27),
                DateTime(2017, 2, 26),
                DateTime(2017, 3, 27),
                DateTime(2017, 4, 26),
                DateTime(2017, 5, 25),
                DateTime(2017, 6, 24),
                DateTime(2017, 7, 23),
                DateTime(2017, 8, 21),
                DateTime(2017, 9, 20),
                DateTime(2017, 10, 19),
                DateTime(2017, 11, 18),
                DateTime(2017, 12, 17),
            ],
        )


    def testMonthlyRscaleStartInLeapYearSkipBackwardDefault(self):

        for rrule in (
            "RSCALE=CHINESE;FREQ=MONTHLY;SKIP=BACKWARD",
            "RSCALE=CHINESE;FREQ=MONTHLY"
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2014, 1, 30) # {C}46501230
            end = DateTime(2018, 1, 1)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2014, 1, 30),
                    DateTime(2014, 2, 28),
                    DateTime(2014, 3, 30),
                    DateTime(2014, 4, 28),
                    DateTime(2014, 5, 28),
                    DateTime(2014, 6, 26),
                    DateTime(2014, 7, 26),
                    DateTime(2014, 8, 24),
                    DateTime(2014, 9, 23),
                    DateTime(2014, 10, 23),
                    DateTime(2014, 11, 21),
                    DateTime(2014, 12, 21),
                    DateTime(2015, 1, 19),
                    DateTime(2015, 2, 18),
                    DateTime(2015, 3, 19),
                    DateTime(2015, 4, 18),
                    DateTime(2015, 5, 17),
                    DateTime(2015, 6, 15),
                    DateTime(2015, 7, 15),
                    DateTime(2015, 8, 13),
                    DateTime(2015, 9, 12),
                    DateTime(2015, 10, 12),
                    DateTime(2015, 11, 11),
                    DateTime(2015, 12, 10),
                    DateTime(2016, 1, 9),
                    DateTime(2016, 2, 7),
                    DateTime(2016, 3, 8),
                    DateTime(2016, 4, 6),
                    DateTime(2016, 5, 6),
                    DateTime(2016, 6, 4),
                    DateTime(2016, 7, 3),
                    DateTime(2016, 8, 2),
                    DateTime(2016, 8, 31),
                    DateTime(2016, 9, 30),
                    DateTime(2016, 10, 30),
                    DateTime(2016, 11, 28),
                    DateTime(2016, 12, 28),
                    DateTime(2017, 1, 27),
                    DateTime(2017, 2, 25),
                    DateTime(2017, 3, 27),
                    DateTime(2017, 4, 25),
                    DateTime(2017, 5, 25),
                    DateTime(2017, 6, 23),
                    DateTime(2017, 7, 22),
                    DateTime(2017, 8, 21),
                    DateTime(2017, 9, 19),
                    DateTime(2017, 10, 19),
                    DateTime(2017, 11, 17),
                    DateTime(2017, 12, 17),
                ],
            )


    def testYearlyLeapDaySkipYes(self):

        recur = Recurrence()
        recur.parse("RSCALE=GREGORIAN;FREQ=YEARLY;SKIP=YES;COUNT=5")
        start = DateTime(2016, 2, 29)
        end = DateTime(2100, 1, 1)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2016, 2, 29),
                DateTime(2020, 2, 29),
                DateTime(2024, 2, 29),
                DateTime(2028, 2, 29),
                DateTime(2032, 2, 29),
            ]
        )


    def testYearlyLeapDaySkipForward(self):

        recur = Recurrence()
        recur.parse("RSCALE=GREGORIAN;FREQ=YEARLY;SKIP=FORWARD;COUNT=5")
        start = DateTime(2016, 2, 29)
        end = DateTime(2100, 1, 1)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2016, 2, 29),
                DateTime(2017, 3, 1),
                DateTime(2018, 3, 1),
                DateTime(2019, 3, 1),
                DateTime(2020, 2, 29),
            ]
        )


    def testYearlyLeapDaySkipBackwardDefault(self):

        for rrule in (
            "RSCALE=GREGORIAN;FREQ=YEARLY;SKIP=BACKWARD;COUNT=5",
            "RSCALE=GREGORIAN;FREQ=YEARLY;COUNT=5",
        ):
            recur = Recurrence()
            recur.parse(rrule)
            start = DateTime(2016, 2, 29)
            end = DateTime(2100, 1, 1)
            items = []
            range = Period(start, end)
            recur.expand(start, range, items)
            self.assertEqual(
                items,
                [
                    DateTime(2016, 2, 29),
                    DateTime(2017, 2, 28),
                    DateTime(2018, 2, 28),
                    DateTime(2019, 2, 28),
                    DateTime(2020, 2, 29),
                ]
            )


    def testChineseMonthlyByMonthDay30SkipYes(self):

        rrule = "RSCALE=CHINESE;FREQ=MONTHLY;BYMONTHDAY=30;SKIP=YES"
        recur = Recurrence()
        recur.parse(rrule)
        start = DateTime(2014, 1, 30, 12, 0, 0)
        end = DateTime(2015, 1, 1, 0, 0, 0)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 1, 30, 12, 0, 0),
                DateTime(2014, 3, 30, 12, 0, 0),
                DateTime(2014, 5, 28, 12, 0, 0),
                DateTime(2014, 7, 26, 12, 0, 0),
                DateTime(2014, 9, 23, 12, 0, 0),
                DateTime(2014, 10, 23, 12, 0, 0),
                DateTime(2014, 12, 21, 12, 0, 0),
            ],
            msg="Failed: {} {}".format(rrule, items,),
        )


    def testChineseMonthlyByMonthDay30SkipBackward(self):

        rrule = "RSCALE=CHINESE;FREQ=MONTHLY;BYMONTHDAY=30;SKIP=BACKWARD"
        recur = Recurrence()
        recur.parse(rrule)
        start = DateTime(2014, 1, 30, 12, 0, 0)
        end = DateTime(2015, 1, 1, 0, 0, 0)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 1, 30, 12, 0, 0),
                DateTime(2014, 2, 28, 12, 0, 0),
                DateTime(2014, 3, 30, 12, 0, 0),
                DateTime(2014, 4, 28, 12, 0, 0),
                DateTime(2014, 5, 28, 12, 0, 0),
                DateTime(2014, 6, 26, 12, 0, 0),
                DateTime(2014, 7, 26, 12, 0, 0),
                DateTime(2014, 8, 24, 12, 0, 0),
                DateTime(2014, 9, 23, 12, 0, 0),
                DateTime(2014, 10, 23, 12, 0, 0),
                DateTime(2014, 11, 21, 12, 0, 0),
                DateTime(2014, 12, 21, 12, 0, 0),
            ],
            msg="Failed: {} {}".format(rrule, items,),
        )


    def testChineseMonthlyByMonthDay30SkipForward(self):

        rrule = "RSCALE=CHINESE;FREQ=MONTHLY;BYMONTHDAY=30;SKIP=FORWARD"
        recur = Recurrence()
        recur.parse(rrule)
        start = DateTime(2014, 1, 30, 12, 0, 0)
        end = DateTime(2015, 1, 1, 0, 0, 0)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 1, 30, 12, 0, 0),
                DateTime(2014, 3, 1, 12, 0, 0),
                DateTime(2014, 3, 30, 12, 0, 0),
                DateTime(2014, 4, 29, 12, 0, 0),
                DateTime(2014, 5, 28, 12, 0, 0),
                DateTime(2014, 6, 27, 12, 0, 0),
                DateTime(2014, 7, 26, 12, 0, 0),
                DateTime(2014, 8, 25, 12, 0, 0),
                DateTime(2014, 9, 23, 12, 0, 0),
                DateTime(2014, 10, 23, 12, 0, 0),
                DateTime(2014, 11, 22, 12, 0, 0),
                DateTime(2014, 12, 21, 12, 0, 0),
            ],
            msg="Failed: {} {}".format(rrule, items,),
        )


    def testChineseMonthlyByMonthDayMinus30SkipYes(self):

        rrule = "RSCALE=CHINESE;FREQ=MONTHLY;BYMONTHDAY=-30;SKIP=YES"
        recur = Recurrence()
        recur.parse(rrule)
        start = DateTime(2014, 1, 30, 12, 0, 0)
        end = DateTime(2015, 1, 1, 0, 0, 0)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 3, 1, 12, 0, 0),
                DateTime(2014, 4, 29, 12, 0, 0),
                DateTime(2014, 6, 27, 12, 0, 0),
                DateTime(2014, 8, 25, 12, 0, 0),
                DateTime(2014, 9, 24, 12, 0, 0),
                DateTime(2014, 11, 22, 12, 0, 0),
            ],
            msg="Failed: {} {}".format(rrule, items,),
        )


    def testChineseMonthlyByMonthDayMinus30SkipBackward(self):

        rrule = "RSCALE=CHINESE;FREQ=MONTHLY;BYMONTHDAY=-30;SKIP=BACKWARD"
        recur = Recurrence()
        recur.parse(rrule)
        start = DateTime(2014, 1, 30, 12, 0, 0)
        end = DateTime(2015, 1, 1, 0, 0, 0)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 1, 30, 12, 0, 0),
                DateTime(2014, 3, 1, 12, 0, 0),
                DateTime(2014, 3, 30, 12, 0, 0),
                DateTime(2014, 4, 29, 12, 0, 0),
                DateTime(2014, 5, 28, 12, 0, 0),
                DateTime(2014, 6, 27, 12, 0, 0),
                DateTime(2014, 7, 26, 12, 0, 0),
                DateTime(2014, 8, 25, 12, 0, 0),
                DateTime(2014, 9, 24, 12, 0, 0),
                DateTime(2014, 10, 23, 12, 0, 0),
                DateTime(2014, 11, 22, 12, 0, 0),
                DateTime(2014, 12, 21, 12, 0, 0),
            ],
            msg="Failed: {} {}".format(rrule, items,),
        )


    def testChineseMonthlyByMonthDayMinus30SkipForward(self):

        rrule = "RSCALE=CHINESE;FREQ=MONTHLY;BYMONTHDAY=-30;SKIP=FORWARD"
        recur = Recurrence()
        recur.parse(rrule)
        start = DateTime(2014, 1, 30, 12, 0, 0)
        end = DateTime(2015, 1, 1, 0, 0, 0)
        items = []
        range = Period(start, end)
        recur.expand(start, range, items)
        self.assertEqual(
            items,
            [
                DateTime(2014, 1, 31, 12, 0, 0),
                DateTime(2014, 3, 1, 12, 0, 0),
                DateTime(2014, 3, 31, 12, 0, 0),
                DateTime(2014, 4, 29, 12, 0, 0),
                DateTime(2014, 5, 29, 12, 0, 0),
                DateTime(2014, 6, 27, 12, 0, 0),
                DateTime(2014, 7, 27, 12, 0, 0),
                DateTime(2014, 8, 25, 12, 0, 0),
                DateTime(2014, 9, 24, 12, 0, 0),
                DateTime(2014, 10, 24, 12, 0, 0),
                DateTime(2014, 11, 22, 12, 0, 0),
                DateTime(2014, 12, 22, 12, 0, 0),
            ],
            msg="Failed: {} {}".format(rrule, items,),
        )
