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


class TestVInstance(unittest.TestCase):
    """
    Basic tests of parsing VINSTANCE components. Actual processing of iCalendar
    data will be tested in L{test_instanceprocessing}.
    """

    data = (
        """BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:1234
DTSTART;VALUE=DATE:20160902
DURATION:PT1H
LOCATION:My office
RRULE:FREQ=DAILY
SUMMARY:Master component
BEGIN:VINSTANCE
RECURRENCE-ID;VALUE=DATE:20160903
INSTANCE-DELETE:#LOCATION
SUMMARY:Override second instance
END:VINSTANCE
END:VEVENT
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
