##
#    Copyright (c) 2011 Cyrus Daboo. All rights reserved.
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
from pycalendar.requeststatusvalue import PyCalendarRequestStatusValue
from pycalendar.property import PyCalendarProperty

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
            req = PyCalendarRequestStatusValue()
            req.parse(item)
            self.assertEqual(req.getText(), item, "Failed to parse and re-generate '%s'" % (item,))

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
            req = PyCalendarProperty()
            req.parse(item)
            self.assertEqual(req.getText(), item + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
