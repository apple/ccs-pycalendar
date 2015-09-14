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
from pycalendar.duration import Duration
from pycalendar.period import Period
import unittest

class TestPeriod(unittest.TestCase):

    test_data = (
        "20000101T000000Z/20000101T010000Z",
        "20000101T000000Z/PT1H",
    )

    def testParseGenerate(self):

        for result in TestPeriod.test_data:
            period = Period.parseText(result)
            self.assertEqual(period.getText(), result)


    def testParseBad(self):

        test_bad_data = (
            "",
            "ABC",
            "20000101T000000Z",
            "20000101T000000Z/",
            "20000101T000000Z/P",
            "20000101T000000Z/2000",
        )
        for data in test_bad_data:
            self.assertRaises(ValueError, Period.parseText, data)


    def testSetUseDuration(self):

        p1 = Period(
            start=DateTime(2000, 1, 1, 0, 0, 0),
            end=DateTime(2000, 1, 1, 1, 0, 0),
        )
        p1.setUseDuration(True)
        self.assertTrue(p1.getText(), "20000101T000000/PT1H")

        p2 = Period(
            start=DateTime(2000, 1, 1, 0, 0, 0),
            duration=Duration(hours=1),
        )
        p2.setUseDuration(False)
        self.assertTrue(p2.getText(), "20000101T000000/20000101T010000")
