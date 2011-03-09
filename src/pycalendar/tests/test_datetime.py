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

from pycalendar.datetime import PyCalendarDateTime
from pycalendar.timezone import PyCalendarTimezone

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
