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

from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions
from pycalendar.icalendar.icudatetime import ICUDateTime
from pycalendar.icalendar.recuriter import RecurrenceIterator
import unittest

class MonthlySkips(object):

    def testMonthlySkipYes(self):

        riter = RecurrenceIterator(self.dt, definitions.eRecurrence_MONTHLY, 1, rscale=self.rscale, skip=definitions.eRecurrence_SKIP_YES)
        results = [riter.next().getText() for _ in range(12)]
        self.assertEqual(
            results,
            [
                "20140131",
                "20140331",
                "20140531",
                "20140731",
                "20140831",
                "20141031",
                "20141231",
                "20150131",
                "20150331",
                "20150531",
                "20150731",
                "20150831",
            ]
        )


    def testMonthlySkipForward(self):

        riter = RecurrenceIterator(self.dt, definitions.eRecurrence_MONTHLY, 1, rscale=self.rscale, skip=definitions.eRecurrence_SKIP_FORWARD)
        results = [riter.next().getText() for _ in range(12)]
        self.assertEqual(
            results,
            [
                "20140131",
                "20140301",
                "20140331",
                "20140501",
                "20140531",
                "20140701",
                "20140731",
                "20140831",
                "20141001",
                "20141031",
                "20141201",
                "20141231",
            ]
        )


    def testMonthlySkipBackward(self):

        riter = RecurrenceIterator(self.dt, definitions.eRecurrence_MONTHLY, 1, rscale=self.rscale, skip=definitions.eRecurrence_SKIP_BACKWARD)
        results = [riter.next().getText() for _ in range(12)]
        self.assertEqual(
            results,
            [
                "20140131",
                "20140228",
                "20140331",
                "20140430",
                "20140531",
                "20140630",
                "20140731",
                "20140831",
                "20140930",
                "20141031",
                "20141130",
                "20141231",
            ]
        )


    def testMonthlySkipBackwardLeap(self):

        riter = RecurrenceIterator(self.dtleap, definitions.eRecurrence_MONTHLY, 1, rscale=self.rscale, skip=definitions.eRecurrence_SKIP_BACKWARD)
        results = [riter.next().getText() for _ in range(12)]
        self.assertEqual(
            results,
            [
                "20160131",
                "20160229",
                "20160331",
                "20160430",
                "20160531",
                "20160630",
                "20160731",
                "20160831",
                "20160930",
                "20161031",
                "20161130",
                "20161231",
            ]
        )



class TestMonthlyDateTime(unittest.TestCase, MonthlySkips):

    def setUp(self):
        self.dt = DateTime(2014, 1, 31)
        self.dtleap = DateTime(2016, 1, 31)
        self.rscale = None



class TestMonthlyGregorianICU(unittest.TestCase, MonthlySkips):

    def setUp(self):
        self.dt = ICUDateTime.fromDateComponents("gregorian", 2014, 1, 31)
        self.dtleap = ICUDateTime.fromDateComponents("gregorian", 2016, 1, 31)
        self.rscale = None



class YearlySkipsOnLeapDay(object):

    def testYearlySkipYes(self):

        riter = RecurrenceIterator(self.dt, definitions.eRecurrence_YEARLY, 1, rscale=self.rscale, skip=definitions.eRecurrence_SKIP_YES)
        results = [riter.next().getText() for _ in range(5)]
        self.assertEqual(
            results,
            [
                "20160229",
                "20200229",
                "20240229",
                "20280229",
                "20320229",
            ]
        )


    def testYearlySkipForward(self):

        riter = RecurrenceIterator(self.dt, definitions.eRecurrence_YEARLY, 1, rscale=self.rscale, skip=definitions.eRecurrence_SKIP_FORWARD)
        results = [riter.next().getText() for _ in range(5)]
        self.assertEqual(
            results,
            [
                "20160229",
                "20170301",
                "20180301",
                "20190301",
                "20200229",
            ]
        )


    def testYearlySkipBackward(self):

        riter = RecurrenceIterator(self.dt, definitions.eRecurrence_YEARLY, 1, rscale=self.rscale, skip=definitions.eRecurrence_SKIP_BACKWARD)
        results = [riter.next().getText() for _ in range(5)]
        self.assertEqual(
            results,
            [
                "20160229",
                "20170228",
                "20180228",
                "20190228",
                "20200229",
            ]
        )



class TestYearlyDateTime(unittest.TestCase, YearlySkipsOnLeapDay):

    def setUp(self):
        self.dt = DateTime(2016, 2, 29)
        self.rscale = None



class TestYearlyGregorianICU(unittest.TestCase, YearlySkipsOnLeapDay):

    def setUp(self):
        self.dt = ICUDateTime.fromDateComponents("gregorian", 2016, 2, 29)
        self.rscale = None



class TestMonthlyChineseICU(unittest.TestCase):

    def testMonthlyStartInLeapYearSkipYes(self):
        dt = ICUDateTime.fromDateComponents("chinese", 4650, 12, 30)

        riter = RecurrenceIterator(dt, definitions.eRecurrence_MONTHLY, 1, rscale=None, skip=definitions.eRecurrence_SKIP_YES)
        results = []
        while True:
            result = riter.next()
            if result.getYear() >= 4655:
                break
            results.append(result.getText())
        self.assertEqual(
            results,
            [
                "{C}46501230",
                "{C}46510230",
                "{C}46510430",
                "{C}46510630",
                "{C}46510830",
                "{C}46510930",
                "{C}46511030",
                "{C}46511230",
                "{C}46520230",
                "{C}46520530",
                "{C}46520730",
                "{C}46520830",
                "{C}46520930",
                "{C}46521130",
                "{C}46530130",
                "{C}46530330",
                "{C}46530630",
                "{C}46530830",
                "{C}46530930",
                "{C}46531130",
                "{C}46531230",
                "{C}46540230",
                "{C}46540430",
                "{C}465406L30",
                "{C}46540830",
                "{C}46541030",
                "{C}46541130",
                "{C}46541230",
            ]
        )


    def testMonthlyStartInLeapYearSkipForward(self):
        dt = ICUDateTime.fromDateComponents("chinese", 4650, 12, 30)

        riter = RecurrenceIterator(dt, definitions.eRecurrence_MONTHLY, 1, rscale=None, skip=definitions.eRecurrence_SKIP_FORWARD)
        results = []
        while True:
            result = riter.next()
            if result.getYear() >= 4655:
                break
            results.append(result.getText())
        self.assertEqual(
            results,
            [
                "{C}46501230",
                "{C}46510201",
                "{C}46510230",
                "{C}46510401",
                "{C}46510430",
                "{C}46510601",
                "{C}46510630",
                "{C}46510801",
                "{C}46510830",
                "{C}46510930",
                "{C}46511001",
                "{C}46511030",
                "{C}46511201",
                "{C}46511230",
                "{C}46520201",
                "{C}46520230",
                "{C}46520401",
                "{C}46520501",
                "{C}46520530",
                "{C}46520701",
                "{C}46520730",
                "{C}46520830",
                "{C}46520930",
                "{C}46521101",
                "{C}46521130",
                "{C}46530101",
                "{C}46530130",
                "{C}46530301",
                "{C}46530330",
                "{C}46530501",
                "{C}46530601",
                "{C}46530630",
                "{C}46530801",
                "{C}46530830",
                "{C}46530930",
                "{C}46531101",
                "{C}46531130",
                "{C}46531230",
                "{C}46540201",
                "{C}46540230",
                "{C}46540401",
                "{C}46540430",
                "{C}46540601",
                "{C}465406L01",
                "{C}465406L30",
                "{C}46540801",
                "{C}46540830",
                "{C}46541001",
                "{C}46541030",
                "{C}46541130",
                "{C}46541230",
            ]
        )


    def testMonthlyStartInLeapYearSkipBackward(self):
        dt = ICUDateTime.fromDateComponents("chinese", 4650, 12, 30)

        riter = RecurrenceIterator(dt, definitions.eRecurrence_MONTHLY, 1, rscale=None, skip=definitions.eRecurrence_SKIP_BACKWARD)
        results = []
        while True:
            result = riter.next()
            if result.getYear() >= 4655:
                break
            results.append(result.getText())
        self.assertEqual(
            results,
            [
                "{C}46501230",
                "{C}46510129",
                "{C}46510230",
                "{C}46510329",
                "{C}46510430",
                "{C}46510529",
                "{C}46510630",
                "{C}46510729",
                "{C}46510830",
                "{C}46510930",
                "{C}465109L29",
                "{C}46511030",
                "{C}46511129",
                "{C}46511230",
                "{C}46520129",
                "{C}46520230",
                "{C}46520329",
                "{C}46520429",
                "{C}46520530",
                "{C}46520629",
                "{C}46520730",
                "{C}46520830",
                "{C}46520930",
                "{C}46521029",
                "{C}46521130",
                "{C}46521229",
                "{C}46530130",
                "{C}46530229",
                "{C}46530330",
                "{C}46530429",
                "{C}46530529",
                "{C}46530630",
                "{C}46530729",
                "{C}46530830",
                "{C}46530930",
                "{C}46531029",
                "{C}46531130",
                "{C}46531230",
                "{C}46540129",
                "{C}46540230",
                "{C}46540329",
                "{C}46540430",
                "{C}46540529",
                "{C}46540629",
                "{C}465406L30",
                "{C}46540729",
                "{C}46540830",
                "{C}46540929",
                "{C}46541030",
                "{C}46541130",
                "{C}46541230",
            ]
        )


    def testMonthlyRscaleStartInLeapYearSkipYes(self):
        dt = ICUDateTime.fromDateComponents("chinese", 4650, 12, 30).toDateTime()

        riter = RecurrenceIterator(dt, definitions.eRecurrence_MONTHLY, 1, rscale="chinese", skip=definitions.eRecurrence_SKIP_YES)
        results = []
        while True:
            result = riter.next()
            if result.getYear() >= 2018:
                break
            results.append(result.getText())
        self.assertEqual(
            results,
            [
                "20140130",
                "20140330",
                "20140528",
                "20140726",
                "20140923",
                "20141023",
                "20141221",
                "20150218",
                "20150418",
                "20150715",
                "20150912",
                "20151012",
                "20151111",
                "20160109",
                "20160308",
                "20160506",
                "20160802",
                "20160930",
                "20161030",
                "20161228",
                "20170127",
                "20170327",
                "20170525",
                "20170821",
                "20171019",
                "20171217",
            ]
        )


    def testMonthlyRscaleStartInLeapYearSkipForward(self):
        dt = ICUDateTime.fromDateComponents("chinese", 4650, 12, 30).toDateTime()

        riter = RecurrenceIterator(dt, definitions.eRecurrence_MONTHLY, 1, rscale="chinese", skip=definitions.eRecurrence_SKIP_FORWARD)
        results = []
        while True:
            result = riter.next()
            if result.getYear() >= 2018:
                break
            results.append(result.getText())
        self.assertEqual(
            results,
            [
                "20140130",
                "20140301",
                "20140330",
                "20140429",
                "20140528",
                "20140627",
                "20140726",
                "20140825",
                "20140923",
                "20141023",
                "20141122",
                "20141221",
                "20150120",
                "20150218",
                "20150320",
                "20150418",
                "20150518",
                "20150616",
                "20150715",
                "20150814",
                "20150912",
                "20151012",
                "20151111",
                "20151211",
                "20160109",
                "20160208",
                "20160308",
                "20160407",
                "20160506",
                "20160605",
                "20160704",
                "20160802",
                "20160901",
                "20160930",
                "20161030",
                "20161129",
                "20161228",
                "20170127",
                "20170226",
                "20170327",
                "20170426",
                "20170525",
                "20170624",
                "20170723",
                "20170821",
                "20170920",
                "20171019",
                "20171118",
                "20171217",
            ]
        )


    def testMonthlyRscaleStartInLeapYearSkipBackward(self):
        dt = ICUDateTime.fromDateComponents("chinese", 4650, 12, 30).toDateTime()

        riter = RecurrenceIterator(dt, definitions.eRecurrence_MONTHLY, 1, rscale="chinese", skip=definitions.eRecurrence_SKIP_BACKWARD)
        results = []
        while True:
            result = riter.next()
            if result.getYear() >= 2018:
                break
            results.append(result.getText())
        self.assertEqual(
            results,
            [
                "20140130",
                "20140228",
                "20140330",
                "20140428",
                "20140528",
                "20140626",
                "20140726",
                "20140824",
                "20140923",
                "20141023",
                "20141121",
                "20141221",
                "20150119",
                "20150218",
                "20150319",
                "20150418",
                "20150517",
                "20150615",
                "20150715",
                "20150813",
                "20150912",
                "20151012",
                "20151111",
                "20151210",
                "20160109",
                "20160207",
                "20160308",
                "20160406",
                "20160506",
                "20160604",
                "20160703",
                "20160802",
                "20160831",
                "20160930",
                "20161030",
                "20161128",
                "20161228",
                "20170127",
                "20170225",
                "20170327",
                "20170425",
                "20170525",
                "20170623",
                "20170722",
                "20170821",
                "20170919",
                "20171019",
                "20171117",
                "20171217",
            ]
        )
