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

from cStringIO import StringIO
from pycalendar.duration import PyCalendarDuration
from pycalendar.parser import ParserContext
import unittest

class TestDuration(unittest.TestCase):

    test_data = (
        (0, "PT0S"),
        (1, "PT1S"),
        (1, "+PT1S"),
        (-1, "-PT1S"),
        (60, "PT1M"),
        (60 + 2, "PT1M2S"),
        (1 * 60 * 60, "PT1H"),
        (1 * 60 * 60 + 2 * 60, "PT1H2M"),
        (1 * 60 * 60 + 1, "PT1H0M1S"),
        (1 * 60 * 60 + 2 * 60 + 1, "PT1H2M1S"),
        (24 * 60 * 60, "P1D"),
        (24 * 60 * 60 + 3 * 60 * 60, "P1DT3H"),
        (24 * 60 * 60 + 2 * 60, "P1DT2M"),
        (24 * 60 * 60 + 3 * 60 * 60 + 2 * 60, "P1DT3H2M"),
        (24 * 60 * 60 + 1, "P1DT1S"),
        (24 * 60 * 60 + 2 * 60 + 1, "P1DT2M1S"),
        (24 * 60 * 60 + 3 * 60 * 60 + 1, "P1DT3H0M1S"),
        (24 * 60 * 60 + 3 * 60 * 60 + 2 * 60 + 1, "P1DT3H2M1S"),
        (14 * 24 * 60 * 60, "P2W"),
        (15 * 24 * 60 * 60, "P15D"),
        (14 * 24 * 60 * 60 + 1, "P14DT1S"),
    )

    def testGenerate(self):

        def _doTest(d, result):

            if result[0] == "+":
                result = result[1:]
            os = StringIO()
            d.generate(os)
            self.assertEqual(os.getvalue(), result)

        for seconds, result in TestDuration.test_data:
            _doTest(PyCalendarDuration(duration=seconds), result)


    def testParse(self):

        for seconds, result in TestDuration.test_data:
            duration = PyCalendarDuration().parseText(result)
            self.assertEqual(duration.getTotalSeconds(), seconds)


    def testParseBad(self):

        test_bad_data = (
            "",
            "ABC",
            "P",
            "PABC",
            "P12",
            "P12D1",
            "P12DTAB",
            "P12DT1HA",
            "P12DT1MA",
            "P12DT1SA",
        )
        for data in test_bad_data:
            self.assertRaises(ValueError, PyCalendarDuration.parseText, data)


    def testRelaxedBad(self):

        test_relaxed_data = (
            ("P12DT", 12 * 24 * 60 * 60, "P12D"),
            ("-P1WT", -7 * 24 * 60 * 60, "-P1W"),
            ("-P1W1D", -7 * 24 * 60 * 60, "-P1W"),
        )
        for text, seconds, result in test_relaxed_data:

            ParserContext.INVALID_DURATION_VALUE = ParserContext.PARSER_FIX
            self.assertEqual(PyCalendarDuration.parseText(text).getTotalSeconds(), seconds)
            self.assertEqual(PyCalendarDuration.parseText(text).getText(), result)

            ParserContext.INVALID_DURATION_VALUE = ParserContext.PARSER_RAISE
            self.assertRaises(ValueError, PyCalendarDuration.parseText, text)
