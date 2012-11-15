##
#    Copyright (c) 2012 Cyrus Daboo. All rights reserved.
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
from pycalendar.utils import encodeParameterValue, decodeParameterValue

class TestUtils(unittest.TestCase):

    def test_encodeParameterValue(self):
        """
        Round trip encodeParameterValue and decodeParameterValue.
        """

        data = (
            ("abc", "abc", None),
            ("\"abc\"", "^'abc^'", None),
            ("abc\ndef", "abc^ndef", None),
            ("abc\rdef", "abc^ndef", "abc\ndef"),
            ("abc\r\ndef", "abc^ndef", "abc\ndef"),
            ("abc\n\tdef", "abc^n^tdef", None),
            ("abc^2", "abc^^2", None),
            ("^abc^", "^^abc^^", None),
        )

        for value, encoded, decoded in data:
            if decoded is None:
                decoded = value
            self.assertEqual(encodeParameterValue(value), encoded)
            self.assertEqual(decodeParameterValue(encoded), decoded)


    def test_decodeParameterValue(self):
        """
        Special cases for decodeParameterValue.
        """

        data = (
            ("^a^bc^", "^a^bc^"),
            ("^^^abc", "^^abc"),
        )

        for value, decoded in data:
            self.assertEqual(decodeParameterValue(value), decoded)
