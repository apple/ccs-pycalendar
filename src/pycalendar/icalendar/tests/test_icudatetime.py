# coding: utf-8
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

import unittest
from pycalendar.datetime import DateTime
from pycalendar.icalendar.icudatetime import ICUDateTime

class TestICUDateTime(unittest.TestCase):
    """
    Test L{ICUDateTime}
    """

    def testRoundtripDateText(self):

        data_date = (
            ("gregorian", 2011, 1, 2, False, "20110102",),
            ("gregorian", 1, 1, 2, False, "00010102",),
            ("chinese", 4651, 1, 1, False, "{C}46510101",),
            ("chinese", 4651, 9, 1, True, "{C}465109L01",),
        )

        for rscale, y, m, d, l, result in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            self.assertEqual(dt.getText(), result, "Failed on: %s" % (result,))


    def testRoundtripDateTime(self):

        data = (
            ("20110102", "gregorian", "20110102"),
            ("20110102T010203Z", "gregorian", "20110102T010203Z"),
            ("00010102", "gregorian", "00010102"),
            ("20140102", "chinese", "{C}46501202"),
            ("20140102T010203Z", "chinese", "{C}46501202T010203Z"),
            ("20141025", "chinese", "{C}465109L02"),
            ("20141025T010203", "chinese", "{C}465109L02T010203"),
        )

        for item, rscale, uitem in data:
            dt = DateTime.parseText(item, False)
            udt = ICUDateTime.fromDateTime(dt, rscale)
            self.assertEqual(udt.getText(), uitem, "Failed on icu: %s" % (uitem,))
            result = udt.toDateTime()
            self.assertEqual(result.getText(), item, "Failed on dt: %s" % (item,))


    def testSetYear(self):

        data_date = (
            ("gregorian", 2012, 1, 2, False, 2013, "20130102", False,),
            ("gregorian", 2012, 2, 29, False, 2013, "20130301", True,),
            ("gregorian", 2012, 2, 29, False, 2016, "20160229", False,),
        )

        for rscale, y, m, d, l, year, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.setYear(year)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(year, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(year, result, result_invalid,))


    def testOffsetYear(self):

        data_date = (
            ("gregorian", 2012, 1, 2, False, 1, "20130102", False,),
            ("gregorian", 2012, 2, 29, False, 1, "20130228", False,),
            ("gregorian", 2012, 2, 29, False, 4, "20160229", False,),
        )

        for rscale, y, m, d, l, year, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.offsetYear(year)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(year, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(year, result, result_invalid,))


    def testSetMonth(self):

        data_date = (
            ("gregorian", 2012, 1, 2, False, 2, "20120202", False,),
            ("gregorian", 2012, 1, 29, False, 2, "20120229", False,),
            ("gregorian", 2012, 1, 31, False, 2, "20120302", True,),
            ("gregorian", 2012, 2, 29, False, 3, "20120329", False,),
        )

        for rscale, y, m, d, l, month, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.setMonth(month)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(month, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(month, result, result_invalid,))


    def testOffsetMonth(self):

        data_date = (
            ("gregorian", 2012, 1, 2, False, 1, "20120202", False,),
            ("gregorian", 2012, 1, 29, False, 1, "20120229", False,),
            ("gregorian", 2012, 1, 31, False, 1, "20120229", False,),
            ("gregorian", 2012, 2, 29, False, 1, "20120329", False,),
        )

        for rscale, y, m, d, l, month, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.offsetMonth(month)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(month, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(month, result, result_invalid,))


    def testSetDay(self):

        data_date = (
            ("gregorian", 2012, 2, 1, False, 2, "20120202", False,),
            ("gregorian", 2012, 2, 1, False, 29, "20120229", False,),
            ("gregorian", 2012, 2, 1, False, 31, "20120302", True,),
        )

        for rscale, y, m, d, l, day, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.setDay(day)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(day, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(day, result, result_invalid,))


    def testOffsetDay(self):

        data_date = (
            ("gregorian", 2012, 2, 1, False, 1, "20120202", False,),
            ("gregorian", 2012, 2, 1, False, 28, "20120229", False,),
            ("gregorian", 2012, 2, 1, False, 30, "20120302", False,),
        )

        for rscale, y, m, d, l, day, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.offsetDay(day)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(day, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(day, result, result_invalid,))


    def testYearDay(self):

        data_date = (
            ("gregorian", 2012, 1, 2, False, 1, False, "20120101", False,),
            ("gregorian", 2012, 1, 2, False, 60, False, "20120229", False,),
            ("gregorian", 2012, 1, 2, False, 366, False, "20121231", False,),
            ("gregorian", 2012, 1, 2, False, 367, False, "20121231", False,),
            ("gregorian", 2012, 1, 2, False, 367, True, "20121231", True,),
            ("gregorian", 2012, 1, 2, False, -1, False, "20121231", False,),
            ("gregorian", 2012, 1, 2, False, -307, False, "20120229", False,),
            ("gregorian", 2012, 1, 2, False, -366, False, "20120101", False,),
            ("gregorian", 2012, 1, 2, False, -367, False, "20120101", False,),
            ("gregorian", 2012, 1, 2, False, -367, True, "20120101", True,),
        )

        for rscale, y, m, d, l, yearday, allow_invalid, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.setYearDay(yearday, allow_invalid=allow_invalid)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(yearday, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(yearday, result, result_invalid,))


    def testMonthDay(self):

        data_date = (
            ("gregorian", 2012, 1, 2, False, 1, False, "20120101", False,),
            ("gregorian", 2012, 1, 31, False, 1, False, "20120101", False,),
            ("gregorian", 2012, 2, 1, False, 31, False, "20120229", False,),
            ("gregorian", 2012, 2, 1, False, 31, True, "20120229", True,),
            ("gregorian", 2012, 1, 2, False, -1, False, "20120131", False,),
            ("gregorian", 2012, 2, 29, False, -29, False, "20120201", False,),
            ("gregorian", 2012, 2, 29, False, -30, False, "20120201", False,),
            ("gregorian", 2012, 2, 29, False, -30, True, "20120201", True,),
        )

        for rscale, y, m, d, l, monthday, allow_invalid, result, result_invalid in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.setMonthDay(monthday, allow_invalid=allow_invalid)
            self.assertEqual(dt.getText(), result, "Failed on: {} {} {}".format(monthday, result, result_invalid,))
            self.assertEqual(dt.invalid(), result_invalid, "Failed invalid on: {} {} {}".format(monthday, result, result_invalid,))


    def testWeekNum(self):

        data_date = (
            ("gregorian", 2012, 1, 3, False, 1, 2, "20120110",),
            ("gregorian", 2014, 1, 3, False, 1, 2, "20140110",),
            ("gregorian", 2012, 1, 1, False, 52, 2, "20120115",),
        )

        for rscale, y, m, d, l, start_weekno, weekno, result in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            self.assertEqual(dt.getWeekNo(), start_weekno)
            dt.setWeekNo(weekno)
            self.assertTrue(dt.isWeekNo(weekno))
            self.assertEqual(dt.getText(), result, "Failed on: {} {} vs {}".format(weekno, result, dt.getText(),))


    def testDayOfWeekInYear(self):

        data_date = (
            ("gregorian", 2012, 1, 3, False, 1, DateTime.SUNDAY, "20120101",),
            ("gregorian", 2012, 1, 3, False, 1, DateTime.MONDAY, "20120102",),
            ("gregorian", 2012, 1, 3, False, 2, DateTime.SUNDAY, "20120108",),
            ("gregorian", 2012, 1, 3, False, 10, DateTime.SUNDAY, "20120304",),
            ("gregorian", 2012, 1, 3, False, -1, DateTime.SUNDAY, "20121230",),
            ("gregorian", 2012, 1, 3, False, -45, DateTime.SUNDAY, "20120226",),
        )

        for rscale, y, m, d, l, offset, day, result in data_date:
            dt = ICUDateTime.fromDateComponents(rscale, y, m, d, l)
            dt.setDayOfWeekInYear(offset, day)
            self.assertEqual(dt.getText(), result, "Failed on: {} vs {}".format(result, dt.getText(),))
