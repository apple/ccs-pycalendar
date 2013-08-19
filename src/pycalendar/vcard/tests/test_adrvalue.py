##
#    Copyright (c) 2011-2012 Cyrus Daboo. All rights reserved.
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

from pycalendar.vcard.adrvalue import AdrValue
from pycalendar.vcard.property import Property
import unittest

class TestAdrValue(unittest.TestCase):

    def testParseValue(self):

        items = (
            ("", ";;;;;;"),
            (";", ";;;;;;"),
            (";;;;;;", ";;;;;;"),
            (";;123 Main Street;Any Town;CA;91921-1234", ";;123 Main Street;Any Town;CA;91921-1234;"),
            (";;;;;;USA", ";;;;;;USA"),
            ("POB1", "POB1;;;;;;"),
            (";EXT", ";EXT;;;;;"),
            (";;123 Main Street,The Cards;Any Town;CA;91921-1234", ";;123 Main Street,The Cards;Any Town;CA;91921-1234;"),
            (";;123 Main\, Street,The Cards;Any Town;CA;91921-1234", ";;123 Main\, Street,The Cards;Any Town;CA;91921-1234;"),
            (";;123 Main\, Street,The\, Cards;Any Town;CA;91921-1234", ";;123 Main\, Street,The\, Cards;Any Town;CA;91921-1234;"),
        )

        for item, result in items:
            req = AdrValue()
            req.parse(item, "vcard")
            test = req.getText()
            self.assertEqual(test, result, "Failed to parse and re-generate '%s'" % (item,))


    def testParseProperty(self):

        items = (
            ("ADR:", "ADR:;;;;;;"),
            ("ADR:;", "ADR:;;;;;;"),
            ("ADR:;;;;;;", "ADR:;;;;;;"),
            ("ADR:;;123 Main Street;Any Town;CA;91921-1234", "ADR:;;123 Main Street;Any Town;CA;91921-1234;"),
            ("ADR:;;;;;;USA", "ADR:;;;;;;USA"),
            ("ADR:POB1", "ADR:POB1;;;;;;"),
            ("ADR:;EXT", "ADR:;EXT;;;;;"),
            ("ADR;VALUE=TEXT:;;123 Main Street;Any Town;CA;91921-1234", "ADR:;;123 Main Street;Any Town;CA;91921-1234;"),
        )

        for item, result in items:
            prop = Property.parseText(item)
            test = prop.getText()
            self.assertEqual(test, result + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
