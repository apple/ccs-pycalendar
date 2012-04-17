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

from pycalendar.calendar import PyCalendar
import cStringIO as StringIO
import difflib
import unittest

class TestXML(unittest.TestCase):
    
    data = (
                (
"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:12345-67890-3
DTSTART:20071114T000000Z
ATTENDEE:mailto:user2@example.com
EXDATE:20081114T000000Z
ORGANIZER:mailto:user1@example.com
RRULE:FREQ=YEARLY
END:VEVENT
X-TEST:Testing
END:VCALENDAR
""".replace("\n", "\r\n"),

"""<?xml version="1.0" encoding="utf-8"?>
<ns0:icalendar xmlns:ns0="urn:ietf:params:xml:ns:icalendar-2.0">
  <ns0:vcalendar>
    <ns0:properties>
      <ns0:version>
        <ns0:text>2.0</ns0:text>
      </ns0:version>
      <ns0:prodid>
        <ns0:text>-//mulberrymail.com//Mulberry v4.0//EN</ns0:text>
      </ns0:prodid>
      <ns0:x-test>
        <ns0:unknown>Testing</ns0:unknown>
      </ns0:x-test>
    </ns0:properties>
    <ns0:components>
      <ns0:vevent>
        <ns0:properties>
          <ns0:uid>
            <ns0:text>12345-67890-3</ns0:text>
          </ns0:uid>
          <ns0:dtstart>
            <ns0:date-time>2007-11-14T00:00:00Z</ns0:date-time>
          </ns0:dtstart>
          <ns0:attendee>
            <ns0:cal-address>mailto:user2@example.com</ns0:cal-address>
          </ns0:attendee>
          <ns0:exdate>
            <ns0:date-time>2008-11-14T00:00:00Z</ns0:date-time>
          </ns0:exdate>
          <ns0:organizer>
            <ns0:cal-address>mailto:user1@example.com</ns0:cal-address>
          </ns0:organizer>
          <ns0:rrule>
            <ns0:recur>
              <ns0:freq>YEARLY</ns0:freq>
            </ns0:recur>
          </ns0:rrule>
        </ns0:properties>
      </ns0:vevent>
    </ns0:components>
  </ns0:vcalendar>
</ns0:icalendar>
""",
                ),
)

    def testGenerateXML(self):

        def _doRoundtrip(caldata, resultdata=None):
            test1 = resultdata if resultdata is not None else caldata

            cal = PyCalendar()
            cal.parse(StringIO.StringIO(caldata))
            
            test2 = cal.getTextXML()

            self.assertEqual(
                test1,
                test2,
                "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
            )

        for item1, item2 in self.data:
            _doRoundtrip(item1, item2)

