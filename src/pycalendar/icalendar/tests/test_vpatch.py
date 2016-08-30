##
#    Copyright (c) 2007-2015 Cyrus Daboo. All rights reserved.
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

from pycalendar.icalendar.calendar import Calendar
import cStringIO as StringIO
import difflib
import unittest


class TestVPatch(unittest.TestCase):
    """
    Basic tests of parsing VPATCH components. Actually patching of iCalendar
    data will be tested in L{test_patch}.
    """

    data = (
        """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//example.com//Example v0.1//EN
BEGIN:VPATCH
UID:A979D282-2CDB-484F-BD63-3972094DFFC0
DTSTAMP:20020101T000000Z
BEGIN:CREATE
TARGET:/VCALENDAR
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:CREATE
BEGIN:UPDATE
TARGET:/VCALENDAR/VEVENT#SUMMARY
SUMMARY:updated
END:UPDATE
BEGIN:DELETE
TARGET:/VCALENDAR/VEVENT#TRANSP
SUMMARY:updated
END:DELETE
END:VPATCH
END:VCALENDAR
""",

    )

    def testRoundtrip(self):

        def _doRoundtrip(caldata, resultdata=None):
            test1 = resultdata if resultdata is not None else caldata

            cal = Calendar()
            cal.parse(StringIO.StringIO(caldata))

            s = StringIO.StringIO()
            cal.generate(s)
            test2 = s.getvalue()

            self.assertEqual(
                test1,
                test2,
                "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
            )

        for item in self.data:
            _doRoundtrip(item.replace("\n", "\r\n"))
