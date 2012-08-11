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

from pycalendar.parser import ParserContext
from pycalendar.urivalue import PyCalendarURIValue
from pycalendar.vcard.property import Property
import unittest

class TestNValue(unittest.TestCase):
    
    def testParseValue(self):
        
        # Restore BACKSLASH_IN_URI_VALUE after test
        old_state = ParserContext.BACKSLASH_IN_URI_VALUE
        self.addCleanup(setattr, ParserContext, "BACKSLASH_IN_URI_VALUE", old_state)

        # Test with BACKSLASH_IN_URI_VALUE = PARSER_FIX
        ParserContext.BACKSLASH_IN_URI_VALUE = ParserContext.PARSER_FIX
        items = (
            ("http://example.com", "http://example.com"),
            ("http://example.com&abd\\,def", "http://example.com&abd,def"),
        )
        
        for item, result in items:
            req = PyCalendarURIValue()
            req.parse(item)
            test = req.getText()
            self.assertEqual(test, result, "Failed to parse and re-generate '%s'" % (item,))

        # Test with BACKSLASH_IN_URI_VALUE = PARSER_ALLOW
        ParserContext.BACKSLASH_IN_URI_VALUE = ParserContext.PARSER_ALLOW
        items = (
            ("http://example.com", "http://example.com"),
            ("http://example.com&abd\\,def", "http://example.com&abd\\,def"),
        )
        
        for item, result in items:
            req = PyCalendarURIValue()
            req.parse(item)
            test = req.getText()
            self.assertEqual(test, result, "Failed to parse and re-generate '%s'" % (item,))

    def testParseProperty(self):
        
        # Restore BACKSLASH_IN_URI_VALUE after test
        old_state = ParserContext.BACKSLASH_IN_URI_VALUE
        self.addCleanup(setattr, ParserContext, "BACKSLASH_IN_URI_VALUE", old_state)

        # Test with BACKSLASH_IN_URI_VALUE = PARSER_FIX
        ParserContext.BACKSLASH_IN_URI_VALUE = ParserContext.PARSER_FIX
        items = (
            ("URL:http://example.com", "URL:http://example.com"),
            ("URL:http://example.com&abd\\,def", "URL:http://example.com&abd,def"),
        )
        
        for item, result in items:
            prop = Property()
            prop.parse(item)
            test = prop.getText()
            self.assertEqual(test, result + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
        
        # Test with BACKSLASH_IN_URI_VALUE = PARSER_ALLOW
        ParserContext.BACKSLASH_IN_URI_VALUE = ParserContext.PARSER_ALLOW
        items = (
            ("URL:http://example.com", "URL:http://example.com"),
            ("URL:http://example.com&abd\\,def", "URL:http://example.com&abd\\,def"),
        )
        
        for item, result in items:
            prop = Property()
            prop.parse(item)
            test = prop.getText()
            self.assertEqual(test, result + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
