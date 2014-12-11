##
#    Copyright (c) 2012-2013 Cyrus Daboo. All rights reserved.
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

from pycalendar.geovalue import GeoValue
from pycalendar.icalendar.property import Property
import unittest

class TestURIValue(unittest.TestCase):

    def testParseValue(self):

        items = (
            ("-12.345;67.890", "-12.345;67.89"),
            ("-12.345\\;67.890", "-12.345;67.89"),
        )

        for item, result in items:
            req = GeoValue()
            req.parse(item, "icalendar")
            test = req.getText()
            self.assertEqual(test, result, "Failed to parse and re-generate '%s'" % (item,))


    def testParseProperty(self):

        items = (
            ("GEO:-12.345;67.890", "GEO:-12.345;67.89"),
            ("GEO:-12.345\\;67.890", "GEO:-12.345;67.89"),
        )

        for item, result in items:
            prop = Property.parseText(item)
            test = prop.getText()
            self.assertEqual(test, result + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
