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

from pycalendar.parser import ParserContext
from pycalendar.icalendar.property import Property
from pycalendar.icalendar.requeststatusvalue import RequestStatusValue
import unittest

class TestRequestStatus(unittest.TestCase):

    def testParseValue(self):

        items = (
            "2.0;Success",
            "2.0;Success\;here",
            "2.0;Success;Extra",
            "2.0;Success\;here;Extra",
            "2.0;Success;Extra\;here",
            "2.0;Success\;here;Extra\;here too",
        )

        for item in items:
            req = RequestStatusValue()
            req.parse(item, "icalendar")
            self.assertEqual(req.getText(), item, "Failed to parse and re-generate '%s'" % (item,))


    def testBadValue(self):

        bad_value = "2.0\;Success"
        ok_value = "2.0;Success"

        # Fix the value
        oldContext = ParserContext.INVALID_REQUEST_STATUS_VALUE
        ParserContext.INVALID_REQUEST_STATUS_VALUE = ParserContext.PARSER_FIX
        req = RequestStatusValue()
        req.parse(bad_value, "icalendar")
        self.assertEqual(req.getText(), ok_value, "Failed to parse and re-generate '%s'" % (bad_value,))

        # Raise the value
        ParserContext.INVALID_REQUEST_STATUS_VALUE = ParserContext.PARSER_RAISE
        req = RequestStatusValue()
        self.assertRaises(ValueError, req.parse, bad_value)

        ParserContext.INVALID_REQUEST_STATUS_VALUE = oldContext


    def testTruncatedValue(self):

        bad_value = "2.0"
        ok_value = "2.0;"

        # Fix the value
        oldContext = ParserContext.INVALID_REQUEST_STATUS_VALUE
        ParserContext.INVALID_REQUEST_STATUS_VALUE = ParserContext.PARSER_FIX
        req = RequestStatusValue()
        req.parse(bad_value, "icalendar")
        self.assertEqual(req.getText(), ok_value, "Failed to parse and re-generate '%s'" % (bad_value,))

        # Raise the value
        ParserContext.INVALID_REQUEST_STATUS_VALUE = ParserContext.PARSER_RAISE
        req = RequestStatusValue()
        self.assertRaises(ValueError, req.parse, bad_value)

        ParserContext.INVALID_REQUEST_STATUS_VALUE = oldContext


    def testParseProperty(self):

        items = (
            "REQUEST-STATUS:2.0;Success",
            "REQUEST-STATUS:2.0;Success\;here",
            "REQUEST-STATUS:2.0;Success;Extra",
            "REQUEST-STATUS:2.0;Success\;here;Extra",
            "REQUEST-STATUS:2.0;Success;Extra\;here",
            "REQUEST-STATUS:2.0;Success\;here;Extra\;here too",
        )

        for item in items:
            req = Property.parseText(item)
            self.assertEqual(req.getText(), item + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
