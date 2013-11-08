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

import unittest
from pycalendar.multivalue import MultiValue
from pycalendar.value import Value

class TestMultiValue(unittest.TestCase):

    def testParseValue(self):

        items = (
            ("", "", 1),
            ("Example", "Example", 1),
            ("Example1,Example2", "Example1,Example2", 2),
        )

        for item, result, count in items:
            req = MultiValue(Value.VALUETYPE_TEXT)
            req.parse(item, "icalendar")
            test = req.getText()
            self.assertEqual(test, result, "Failed to parse and re-generate '%s'" % (item,))
            self.assertEqual(len(req.mValues), count, "Failed to parse and re-generate '%s'" % (item,))


    def testSetValue(self):

        req = MultiValue(Value.VALUETYPE_TEXT)
        req.parse("Example1, Example2", "icalendar")
        req.setValue(("Example3", "Example4",))
        test = req.getText()
        self.assertEqual(test, "Example3,Example4")
