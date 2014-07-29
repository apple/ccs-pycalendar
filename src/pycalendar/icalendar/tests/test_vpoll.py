##
#    Copyright (c) 2007-2013 Cyrus Daboo. All rights reserved.
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

class TestCalendar(unittest.TestCase):

    data = (
        """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VPOLL
UID:A979D282-2CDB-484F-BD63-3972094DFFC0
DTSTAMP:20020101T000000Z
ORGANIZER:mailto:user01@example.com
POLL-MODE:BASIC
POLL-PROPERTIES:DTSTART,DTEND
VOTER;CN=User 02:mailto:user02@example.com
VOTER;CN=User 03:mailto:user03@example.com
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20130101
DTEND;VALUE=DATE:20130102
DTSTAMP:20020101T000000Z
POLL-ITEM-ID:1
SUMMARY:Party option #1
END:VEVENT
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20130201
DTEND;VALUE=DATE:20130202
DTSTAMP:20020101T000000Z
POLL-ITEM-ID:2
SUMMARY:Party option #2
END:VEVENT
END:VPOLL
END:VCALENDAR
""",

        """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:REPLY
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VPOLL
UID:A979D282-2CDB-484F-BD63-3972094DFFC0
DTSTAMP:20020101T000000Z
ORGANIZER:mailto:user01@example.com
POLL-ITEM-ID;PUBLIC-COMMENT=Not ideal;RESPONSE=50:1
POLL-ITEM-ID;PUBLIC-COMMENT=Perfect;RESPONSE=100:2
POLL-MODE:BASIC
POLL-PROPERTIES:DTSTART,DTEND
VOTER;CN=User 02:mailto:user02@example.com
END:VPOLL
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
