##
#    Copyright (c) 2007 Cyrus Daboo. All rights reserved.
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
from pycalendar.calendar import PyCalendar

import StringIO
import unittest

class TestCalendar(unittest.TestCase):
    
    def testRoundtrip(self):
        
        data = (
"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
VERSION:2.0
BEGIN:VEVENT
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
DTSTART;VALUE=DATE:20020101
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
END:VEVENT
END:VCALENDAR
""",

"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
VERSION:2.0
X-WR-CALNAME:PayDay
BEGIN:VTIMEZONE
LAST-MODIFIED:20040110T032845Z
TZID:US/Eastern
BEGIN:DAYLIGHT
DTSTART:20000404T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20001026T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
DTSTAMP:20050211T173501Z
DTSTART;VALUE=DATE:20040227
RRULE:FREQ=MONTHLY;BYDAY=-1MO,-1TU,-1WE,-1TH,-1FR;BYSETPOS=-1
SUMMARY:PAY DAY
UID:DC3D0301C7790B38631F1FBB@ninevah.local
END:VEVENT
END:VCALENDAR
""",
)

        def _doRoundtrip(caldata):
            cal = PyCalendar()
            cal.parse(StringIO.StringIO(caldata))
            
            s = StringIO.StringIO()
            cal.generate(s)
            
            self.assertEqual(caldata, s.getvalue())

        for item in data:
            _doRoundtrip(item)
