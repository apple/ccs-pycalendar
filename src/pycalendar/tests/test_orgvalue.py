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

from pycalendar.orgvalue import OrgValue
from pycalendar.vcard.property import Property
import unittest

class TestNValue(unittest.TestCase):

    def testParseValue(self):

        items = (
            ("", ""),
            ("Example", "Example"),
            ("Example\, Inc.", "Example\, Inc."),
            ("Example\; Inc;Dept. of Silly Walks", "Example\; Inc;Dept. of Silly Walks"),
        )

        for item, result in items:
            req = OrgValue()
            req.parse(item)
            test = req.getText()
            self.assertEqual(test, result, "Failed to parse and re-generate '%s'" % (item,))


    def testParseProperty(self):

        items = (
            ("ORG:", "ORG:"),
            ("ORG:Example", "ORG:Example"),
            ("ORG:Example\, Inc.", "ORG:Example\, Inc."),
            ("ORG:Example\; Inc;Dept. of Silly Walks", "ORG:Example\; Inc;Dept. of Silly Walks"),
            ("ORG;VALUE=TEXT:Example", "ORG:Example"),
        )

        for item, result in items:
            prop = Property()
            prop.parse(item)
            test = prop.getText()
            self.assertEqual(test, result + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
