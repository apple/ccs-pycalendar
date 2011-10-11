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

from pycalendar.datetime import PyCalendarDateTime
from pycalendar.timezone import PyCalendarTimezone
import unittest

class TestDateTime(unittest.TestCase):
    
    def testDuplicateASUTC(self):
        
        items = (
            (
                PyCalendarDateTime(2011, 1, 1, 0, 0, 0, tzid=PyCalendarTimezone(utc=True)),
                PyCalendarDateTime(2011, 1, 1, 0, 0, 0, tzid=PyCalendarTimezone(utc=True)),
            ),
            (
                PyCalendarDateTime(2011, 1, 1, 0, 0, 0),
                PyCalendarDateTime(2011, 1, 1, 0, 0, 0),
            ),
            (
                PyCalendarDateTime(2011, 1, 1),
                PyCalendarDateTime(2011, 1, 1),
            )
        )
        
        for item, result in items:
            dup = item.duplicateAsUTC()
            self.assertEqual(str(dup), str(result), "Failed to convert '%s'" % (item,))

    def testDuplicateInSet(self):
        
        s = set(
            (
                PyCalendarDateTime(2011, 1, 1, 0, 0, 0, tzid=PyCalendarTimezone(utc=True)),
                PyCalendarDateTime(2011, 1, 2, 0, 0, 0, tzid=PyCalendarTimezone(utc=True)),
            )
        )
        
        self.assertTrue(PyCalendarDateTime(2011, 1, 1, 0, 0, 0, tzid=PyCalendarTimezone(utc=True)) in s)
        self.assertFalse(PyCalendarDateTime(2011, 1, 3, 0, 0, 0, tzid=PyCalendarTimezone(utc=True)) in s)

    def testRoundtrip(self):
        
        data1 = (
            "20110102",
            "20110103T121212",
            "20110103T121212Z",
            "00010102",
            "00010103T121212",
            "00010103T121212Z",
        )
        
        data2 = (
            ("20110102", "20110102"),
            ("2011-01-02", "20110102"),
            ("20110103T121212", "20110103T121212"),
            ("2011-01-03T12:12:12", "20110103T121212"),
            ("20110103T121212Z", "20110103T121212Z"),
            ("2011-01-03T12:12:12Z", "20110103T121212Z"),
            ("20110103T121212+0100", "20110103T121212+0100"),
            ("2011-01-03T12:12:12-0500", "20110103T121212-0500"),
            ("20110103T121212,123", "20110103T121212"),
            ("2011-01-03T12:12:12,123", "20110103T121212"),
            ("20110103T121212,123Z", "20110103T121212Z"),
            ("2011-01-03T12:12:12,123Z", "20110103T121212Z"),
            ("20110103T121212,123+0100", "20110103T121212+0100"),
            ("2011-01-03T12:12:12,123-0500", "20110103T121212-0500"),
        )

        for item in data1:
            dt = PyCalendarDateTime.parseText(item, False)
            self.assertEqual(dt.getText(), item, "Failed on: %s" % (item,))
        
        for item, result in data2:
            dt = PyCalendarDateTime.parseText(item, True)
            self.assertEqual(dt.getText(), result, "Failed on: %s" % (item,))
        
    def testBadParse(self):
        
        data1 = (
            "2011",
            "201101023",
            "20110103t121212",
            "20110103T1212",
            "20110103T1212123",
            "20110103T121212A",
            "2011-01-03T121212Z",
            "20110103T12:12:12Z",
            "20110103T121212+0500",
            "   10102",
            "   10102T010101",
            "2011 102",
            "201101 3T121212",
            "-1110102",
            "2011-102",
            "201101-3T121212",
        )
        data2 = (
            "2011-01+02",
            "20110103T12-12-12",
            "2011-01-03T12:12:12,",
            "2011-01-03T12:12:12,ABC",
            "20110103T12:12:12-1",
        )

        for item in data1:
            self.assertRaises(ValueError, PyCalendarDateTime.parseText, item, False)
        
        for item in data2:
            self.assertRaises(ValueError, PyCalendarDateTime.parseText, item, False)
        
