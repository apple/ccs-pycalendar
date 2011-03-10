##
#    Copyright (c) 2007-2011 Cyrus Daboo. All rights reserved.
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

from pycalendar.property import PyCalendarProperty
from pycalendar.exceptions import PyCalendarInvalidProperty

class TestProperty(unittest.TestCase):
    
    test_data = (
        # Different value types
        "ATTACH;VALUE=BINARY:VGVzdA==",
        "ORGANIZER:mailto:jdoe@example.com",
        "DTSTART;TZID=US/Eastern:20060226T120000",
        "DTSTART;VALUE=DATE:20060226",
        "DTSTART:20060226T120000Z",
        "X-FOO:BAR",
        "DURATION:PT10M",
        "SEQUENCE:1",
        "RDATE:20060226T120000Z,20060227T120000Z",
        "FREEBUSY:20060226T120000Z/20060227T120000Z",
        "SUMMARY:Some \\ntext",
        "RRULE:FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,TH;BYSETPOS=-1",
        "REQUEST-STATUS:2.0;Success",
        "URI:http://www.example.com",
        "TZOFFSETFROM:-0500",
        
        # Various parameters
        "DTSTART;TZID=\"Somewhere, else\":20060226T120000",
        "DTSTART;VALUE=DATE:20060226",
        "ATTENDEE;PARTSTAT=ACCEPTED;ROLE=CHAIR:mailto:jdoe@example.com",
    )
    
    def testParseGenerate(self):
        
        for data in TestProperty.test_data:
            prop = PyCalendarProperty()
            try:
                prop.parse(data)
            except Exception, e:
                print data, e
            propstr = str(prop)
            self.assertEqual(propstr[:-2], data, "Failed parse/generate: %s to %s" % (data, propstr,))
    
    def testEquality(self):
        
        for data in TestProperty.test_data:
            prop1 = PyCalendarProperty()
            prop1.parse(data)
            prop2 = PyCalendarProperty()
            prop2.parse(data)
            self.assertEqual(prop1, prop2, "Failed equality: %s" % (data,))
    
    def testParseBad(self):
        
        test_bad_data = (
            "DTSTART;TZID=US/Eastern:abc",
            "DTSTART;VALUE=DATE:20060226T",
            "DTSTART:20060226T120000A",
            "X-FOO;:BAR",
            "DURATION:A",
            "SEQUENCE:b",
            "RDATE:20060226T120000Z;20060227T120000Z",
            "FREEBUSY:20060226T120000Z/ABC",
            "SUMMARY:Some \\qtext",
            "RRULE:FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,VE;BYSETPOS=-1",
            "REQUEST-STATUS:2.0,Success",
            "TZOFFSETFROM:-050",
        )
        for data in test_bad_data:
            prop = PyCalendarProperty()
            print data
            self.assertRaises(PyCalendarInvalidProperty, prop.parse, data)
