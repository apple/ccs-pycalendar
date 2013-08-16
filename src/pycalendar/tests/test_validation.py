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

from pycalendar.icalendar.property import Property
from pycalendar.validation import partial, PropertyValueChecks
import unittest

class TestValidation(unittest.TestCase):

    def test_partial(self):


        def _test(a, b):
            return (a, b)

        self.assertEqual(partial(_test, "a", "b")(), ("a", "b",))
        self.assertEqual(partial(_test, "a")("b"), ("a", "b",))
        self.assertEqual(partial(_test)("a", "b"), ("a", "b",))


    def test_stringValue(self):

        props = (
            ("SUMMARY:Test", "Test", True,),
            ("SUMMARY:Test", "TEST", True,),
            ("DTSTART:20110623T174806", "Test", False),
        )

        for prop, test, result in props:
            property = Property()
            property.parse(prop)
            self.assertEqual(PropertyValueChecks.stringValue(test, property), result)


    def test_alwaysUTC(self):

        props = (
            ("SUMMARY:Test", False,),
            ("DTSTART:20110623T174806", False),
            ("DTSTART;VALUE=DATE:20110623", False),
            ("DTSTART:20110623T174806Z", True),
        )

        for prop, result in props:
            property = Property()
            property.parse(prop)
            self.assertEqual(PropertyValueChecks.alwaysUTC(property), result)


    def test_numericRange(self):

        props = (
            ("SUMMARY:Test", 0, 100, False,),
            ("PERCENT-COMPLETE:0", 0, 100, True,),
            ("PERCENT-COMPLETE:100", 0, 100, True,),
            ("PERCENT-COMPLETE:50", 0, 100, True,),
            ("PERCENT-COMPLETE:200", 0, 100, False,),
            ("PERCENT-COMPLETE:-1", 0, 100, False,),
        )

        for prop, low, high, result in props:
            property = Property()
            property.parse(prop)
            self.assertEqual(PropertyValueChecks.numericRange(low, high, property), result)


    def test_positiveIntegerOrZero(self):

        props = (
            ("SUMMARY:Test", False,),
            ("REPEAT:0", True,),
            ("REPEAT:100", True,),
            ("REPEAT:-1", False,),
        )

        for prop, result in props:
            property = Property()
            property.parse(prop)
            self.assertEqual(PropertyValueChecks.positiveIntegerOrZero(property), result)
