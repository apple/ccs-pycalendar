# -*- coding: utf-8 -*-
##
#    Copyright (c) 2015 Cyrus Daboo. All rights reserved.
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

from pycalendar.datetime import DateTime
from pycalendar.icalendar.calendar import Calendar
from pycalendar.icalendar.path import Path
import unittest


class TestPath(unittest.TestCase):

    test_data = (
        # Valid

        # Components
        (
            "/VCALENDAR",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
            ],
            None,
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            None,
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234]"),
            ],
            None,
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234%5D4567]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234]4567]"),
            ],
            None,
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            None,
            None,
            None,
        ),

        # Relative Components
        (
            "/VEVENT[UID=1234%5D4567]",
            True,
            [
                Path.ComponentSegment("VEVENT[UID=1234]4567]"),
            ],
            None,
            None,
            None,
        ),

        # Properties
        (
            "/VCALENDAR#VERSION",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
            ],
            Path.PropertySegment("VERSION"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT#SUMMARY",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("SUMMARY"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT#SUMMARY[=abc]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("SUMMARY", "=abc"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT#SUMMARY[=a%5Dc]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("SUMMARY", "=a]c"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT#SUMMARY[!abc]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("SUMMARY", "!abc"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234]#SUMMARY",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234]"),
            ],
            Path.PropertySegment("SUMMARY"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234]#SUMMARY[=abc]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234]"),
            ],
            Path.PropertySegment("SUMMARY", "=abc"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]#SUMMARY",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            Path.PropertySegment("SUMMARY"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]#SUMMARY[=abc]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            Path.PropertySegment("SUMMARY", "=abc"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]#DESCRIPTION[@LANGUAGE]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            Path.PropertySegment("DESCRIPTION", "@LANGUAGE"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]#DESCRIPTION[@LANGUAGE=en_US]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            Path.PropertySegment("DESCRIPTION", "@LANGUAGE=en_US"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]#DESCRIPTION[@LANGUAGE!en_US]",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            Path.PropertySegment("DESCRIPTION", "@LANGUAGE!en_US"),
            None,
            None,
        ),
        (
            "/VCALENDAR/VEVENT#EXDATE=20160903",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("EXDATE"),
            None,
            "20160903",
        ),

        # Parameters
        (
            "/VCALENDAR#VERSION;VALUE",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
            ],
            Path.PropertySegment("VERSION"),
            Path.ParameterSegment("VALUE"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT#ATTENDEE;PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("ATTENDEE"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT#ATTENDEE[=abc];PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("ATTENDEE", "=abc"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT#ATTENDEE[=a%5Dc];PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("ATTENDEE", "=a]c"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT#ATTENDEE[!abc];PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("ATTENDEE", "!abc"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234]#ATTENDEE;PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234]"),
            ],
            Path.PropertySegment("ATTENDEE"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234]#ATTENDEE[=abc];PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234]"),
            ],
            Path.PropertySegment("ATTENDEE", "=abc"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]#ATTENDEE;PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            Path.PropertySegment("ATTENDEE"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT[UID=1234][RID=20150907T120000Z]#ATTENDEE[=abc];PARTSTAT",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT[UID=1234][RID=20150907T120000Z]"),
            ],
            Path.PropertySegment("ATTENDEE", "=abc"),
            Path.ParameterSegment("PARTSTAT"),
            None,
        ),
        (
            "/VCALENDAR/VEVENT#ATTENDEE;MEMBER=mailto:cyrus@example.com",
            True,
            [
                Path.ComponentSegment("VCALENDAR"),
                Path.ComponentSegment("VEVENT"),
            ],
            Path.PropertySegment("ATTENDEE"),
            Path.ParameterSegment("MEMBER"),
            "mailto:cyrus@example.com",
        ),

        # Invalid
    )

    def testParse(self):

        for ctr, item in enumerate(TestPath.test_data):
            strpath, valid, components, property, parameter, value = item
            try:
                path = Path(strpath)
            except ValueError:
                self.assertFalse(valid, msg="Failed #{} {}".format(ctr + 1, strpath))
            else:
                self.assertTrue(valid, msg="Failed #{} {}".format(ctr + 1, strpath))
                self.assertEqual(path.components, components, msg="Failed #{} {}".format(ctr + 1, strpath))
                self.assertEqual(path.property, property, msg="Failed #{} {}".format(ctr + 1, strpath))
                self.assertEqual(path.parameter, parameter, msg="Failed #{} {}".format(ctr + 1, strpath))
                self.assertEqual(path.value, value, msg="Failed #{} {}".format(ctr + 1, strpath))
                self.assertEqual(str(path), strpath, msg="Failed #{}: {}".format(ctr + 1, strpath))

    def testType(self):

        data = [
            ("/VCALENDAR", True, False, False, False, False,),
            ("/VCALENDAR/VEVENT", True, False, False, False, False,),
            ("/VCALENDAR/VEVENT#SUMMARY", False, True, False, False, False,),
            ("/VCALENDAR/VEVENT#SUMMARY;X-PARAM", False, False, True, False, False,),
            ("/VCALENDAR/VEVENT#SUMMARY=FOO", False, False, False, True, False,),
            ("/VCALENDAR/VEVENT#SUMMARY;X-PARAM=BAR", False, False, False, False, True,),
        ]

        for strpath, isComponent, isProperty, isParameter, isPropertyValue, isParameterValue in data:
            path = Path(strpath)
            self.assertEqual(path.targetComponent(), isComponent)
            self.assertEqual(path.targetProperty(), isProperty)
            self.assertEqual(path.targetParameter(), isParameter)
            self.assertEqual(path.targetPropertyValue(), isPropertyValue)
            self.assertEqual(path.targetParameterValue(), isParameterValue)

    def testStr(self):

        data = [
            "/VCALENDAR",
            "/VCALENDAR/VEVENT",
            "/VCALENDAR/VEVENT[UID=ABC]",
            "/VCALENDAR/VEVENT[UID=ABC][RID=20160830]",
            "/VCALENDAR/VEVENT[UID=ABC][RID=M]",
            "/VCALENDAR/VEVENT[RID=20160830]",
            "/VCALENDAR/VEVENT#SUMMARY",
            "/VCALENDAR/VEVENT#SUMMARY[=XYZ]",
            "/VCALENDAR/VEVENT#SUMMARY[!XYZ]",
            "/VCALENDAR/VEVENT#SUMMARY;X-PARAM",
        ]

        for strpath in data:
            path = Path(strpath)
            self.assertEqual(strpath, str(path), msg="Mismatch for: {} vs {}".format(strpath, str(path)))

    def testMatch_Components_Simple(self):

        icalendar = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//example.com//Example v0.1//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
"""

        calendar = Calendar.parseText(icalendar.replace("\n", "\r\n"))
        path = Path("/VCALENDAR")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar)

        path = Path("/VCALENDAR/VEVENT")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar.getComponents("VEVENT")[0])

        path = Path("/VCALENDAR/VEVENT[UID=123]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT[UID=C3184A66-1ED0-11D9-A5E0-000A958A3252]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar.getComponents("VEVENT")[0])

        path = Path("/VCALENDAR/VEVENT[UID=123][RID=20150101T000000Z]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT[UID=C3184A66-1ED0-11D9-A5E0-000A958A3252][RID=M]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar.getComponents("VEVENT")[0])

        path = Path("/VCALENDAR/VEVENT[UID=123][RID=M]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT[UID=C3184A66-1ED0-11D9-A5E0-000A958A3252][RID=20020101]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)

        path = Path("/VCALENDAR/VEVENT[UID=C3184A66-1ED0-11D9-A5E0-000A958A3252][RID=M]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar.getComponents("VEVENT")[0])

    def testMatch_Components_Multiple(self):

        icalendar = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//example.com//Example v0.1//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY
SUMMARY:New Year's Day
END:VEVENT
BEGIN:VEVENT
UID:165EF135-BA92-435A-88C9-562F95030908
DTSTART;VALUE=DATE:20020401
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY
SUMMARY:April Fool's Day
END:VEVENT
BEGIN:VEVENT
UID:5EA5AF47-77F5-4EEE-9944-69651C97755B
DTSTART;VALUE=DATE:20020921
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY
SUMMARY:Birthday
END:VEVENT
END:VCALENDAR
"""

        calendar = Calendar.parseText(icalendar.replace("\n", "\r\n"))
        components_by_uid = dict([(component.getUID(), component) for component in calendar.getComponents()])

        path = Path("/VCALENDAR")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar)

        path = Path("/VCALENDAR/VEVENT")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 3)
        self.assertEqual(
            set([item.getUID() for item in matched]),
            set(components_by_uid.keys()),
        )

        path = Path("/VCALENDAR/VEVENT[UID=123]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        for key in components_by_uid.keys():
            path = Path("/VCALENDAR/VEVENT[UID={key}]".format(key=key))
            matched = path.match(calendar)
            self.assertEqual(len(matched), 1)
            self.assertIs(matched[0], components_by_uid[key])

        path = Path("/VCALENDAR/VEVENT[UID=123][RID=20150101T000000Z]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT[UID=C3184A66-1ED0-11D9-A5E0-000A958A3252][RID=M]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            components_by_uid["C3184A66-1ED0-11D9-A5E0-000A958A3252"],
        )

        for key in components_by_uid.keys():
            path = Path("/VCALENDAR/VEVENT[UID={key}][RID=20150101T000000Z]".format(key=key))
            matched = path.match(calendar)
            self.assertEqual(len(matched), 1)

        for key in components_by_uid.keys():
            path = Path("/VCALENDAR/VEVENT[UID={key}][RID=M]".format(key=key))
            matched = path.match(calendar)
            self.assertEqual(len(matched), 1)
            self.assertIs(matched[0], components_by_uid[key])

    def testMatch_Components_Recurring(self):

        icalendar = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//example.com//Example v0.1//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART:20020101T120000Z
DURATION:PT1H
DTSTAMP:20020101T000000Z
RRULE:FREQ=DAILY
SUMMARY:Meeting
END:VEVENT
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
RECURRENCE-ID:20020102T120000Z
DTSTART:20020102T130000Z
DURATION:PT1H
DTSTAMP:20020101T000000Z
SUMMARY:Meeting #2
END:VEVENT
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
RECURRENCE-ID:20020103T120000Z
DTSTART:20020103T140000Z
DURATION:PT1H
DTSTAMP:20020101T000000Z
SUMMARY:Meeting #3
END:VEVENT
END:VCALENDAR
"""

        calendar = Calendar.parseText(icalendar.replace("\n", "\r\n"))
        components_by_rid = dict([(component.getRecurrenceID(), component) for component in calendar.getComponents()])

        path = Path("/VCALENDAR")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar)

        path = Path("/VCALENDAR/VEVENT")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 3)
        self.assertEqual(
            set([item.getRecurrenceID() for item in matched]),
            set(components_by_rid.keys()),
        )

        path = Path("/VCALENDAR/VEVENT[UID=123][RID=20150101T000000Z]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        for key in components_by_rid.keys():
            path = Path("/VCALENDAR/VEVENT[UID=C3184A66-1ED0-11D9-A5E0-000A958A3252][RID={key}]".format(key=key if key else "M"))
            matched = path.match(calendar)
            self.assertEqual(len(matched), 1)
            self.assertIs(matched[0], components_by_rid[key])

        path = Path("/VCALENDAR/VEVENT[UID=C3184A66-1ED0-11D9-A5E0-000A958A3252][RID=M]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], components_by_rid[None])

    def testMatch_Components_Relative(self):

        icalendar = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//example.com//Example v0.1//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
UID:4567
ACTION:DISPLAY
TRIGGER:-PT30M
DESCRIPTION:Time to leave (30 mins)
END:VALARM
BEGIN:VALARM
UID:89AB
ACTION:DISPLAY
TRIGGER:-PT5M
DESCRIPTION:Time to leave (5 mins)
END:VALARM
END:VEVENT
END:VCALENDAR
"""

        calendar = Calendar.parseText(icalendar.replace("\n", "\r\n"))
        path = Path("/VEVENT")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertIs(matched[0], calendar.getComponents("VEVENT")[0])

        path = Path("/VEVENT/VALARM")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 2)

    def testMatch_Properties_Simple(self):

        icalendar = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//example.com//Example v0.1//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
"""

        calendar = Calendar.parseText(icalendar.replace("\n", "\r\n"))
        path = Path("/VCALENDAR#VERSION")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            (calendar, calendar.getProperties("VERSION")[0],),
        )

        path = Path("/VCALENDAR#FOOBAR")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT#SUMMARY")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            (calendar.getComponents()[0], calendar.getComponents()[0].getProperties("SUMMARY")[0],),
        )

        # Non-existent - for_update changes behavior
        path = Path("/VCALENDAR/VEVENT#FOOBAR")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT#FOOBAR")
        matched = path.match(calendar, for_update=True)
        self.assertEqual(len(matched), 1)

        path = Path("/VCALENDAR/VEVENT#SUMMARY[=New Year's Day]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            (calendar.getComponents()[0], calendar.getComponents()[0].getProperties("SUMMARY")[0],),
        )

        # Non-existent - for_update does not change behavior
        path = Path("/VCALENDAR/VEVENT#SUMMARY[=New Years Day]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT#SUMMARY[=New Years Day]")
        matched = path.match(calendar, for_update=True)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT#DTSTART[=20020101]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            (calendar.getComponents()[0], calendar.getComponents()[0].getProperties("DTSTART")[0],),
        )

        path = Path("/VCALENDAR/VEVENT#RRULE[=20020101]")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

    def testMatch_Parameters_Simple(self):

        icalendar = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//example.com//Example v0.1//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
"""

        calendar = Calendar.parseText(icalendar.replace("\n", "\r\n"))

        path = Path("/VCALENDAR/VEVENT#SUMMARY;X-PARAM")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            (calendar.getComponents()[0], calendar.getComponents()[0].getProperties("SUMMARY")[0], "X-PARAM",)
        )

        path = Path("/VCALENDAR/VEVENT#FOOBAR;X-PARAM")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT#SUMMARY[=New Year's Day];X-PARAM")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            (calendar.getComponents()[0], calendar.getComponents()[0].getProperties("SUMMARY")[0], "X-PARAM",)
        )

        path = Path("/VCALENDAR/VEVENT#SUMMARY[=New Years Day];X-PARAM")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 0)

        path = Path("/VCALENDAR/VEVENT#DTSTART[=20020101];VALUE")
        matched = path.match(calendar)
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0],
            (calendar.getComponents()[0], calendar.getComponents()[0].getProperties("DTSTART")[0], "VALUE",)
        )


class TestComponentSegment(unittest.TestCase):

    test_data = (
        # Valid
        ("VCALENDAR", True, "VCALENDAR", None, None, None,),
        ("VCALENDAR[UID=1234]", True, "VCALENDAR", "1234", None, None,),
        ("VCALENDAR[UID=1234%5D4567]", True, "VCALENDAR", "1234]4567", None, None,),
        ("VCALENDAR[UID=1234][RID=M]", True, "VCALENDAR", "1234", True, None,),
        ("VCALENDAR[UID=1234][RID=20150907T120000Z]", True, "VCALENDAR", "1234", True, "20150907T120000Z",),

        # Invalid
        ("VCALENDAR[]", False, None, None, None, None,),
        ("VCALENDAR[foo]", False, None, None, None, None,),
        ("VCALENDAR[foo=bar]", False, None, None, None, None,),
        ("VCALENDAR[UID=", False, None, None, None, None,),
        ("VCALENDAR[UID=1234][]", False, None, None, None, None,),
        ("VCALENDAR[UID=1234][foo=bar]", False, None, None, None, None,),
        ("VCALENDAR[UID=1234][RID=M", False, None, None, None, None,),
    )

    def testParse(self):

        for ctr, item in enumerate(TestComponentSegment.test_data):
            segment, valid, name, uid, rid, rid_value = item
            try:
                component = Path.ComponentSegment(segment)
            except ValueError:
                self.assertFalse(valid, msg="Failed #{}".format(ctr + 1))
            else:
                self.assertTrue(valid, msg="Failed #{}".format(ctr + 1))
                self.assertEqual(component.name, name, msg="Failed #{}".format(ctr + 1))
                self.assertEqual(component.uid, uid, msg="Failed #{}".format(ctr + 1))
                self.assertEqual(component.rid, rid, msg="Failed #{}".format(ctr + 1))
                self.assertEqual(component.rid_value, DateTime.parseText(rid_value) if rid_value else None, msg="Failed #{}".format(ctr + 1))


class TestPropertySegment(unittest.TestCase):

    test_data = (
        # Valid
        ("STATUS", None, True, "STATUS", None,),
        ("STATUS", "=COMPLETED", True, "STATUS", ("=", "COMPLETED",),),
        ("STATUS", "!COMPLETED", True, "STATUS", ("!", "COMPLETED",),),
        ("SUMMARY", "=a%5Db", True, "SUMMARY", ("=", "a]b",),),
        ("STATUS", "@RSVP", True, "STATUS", ("@", "RSVP", None, None, ),),
        ("STATUS", "@RSVP=TRUE", True, "STATUS", ("@", "RSVP", "=", "TRUE",),),
        ("STATUS", "@RSVP!TRUE", True, "STATUS", ("@", "RSVP", "!", "TRUE",),),

        # Invalid
        ("", None, False, None, None,),
        ("STATUS", "", False, None, None,),
        ("STATUS", "foo", False, None, None,),
        ("STATUS", "=", False, None, None,),
    )

    def testParse(self):

        for ctr, item in enumerate(TestPropertySegment.test_data):
            segment, match, valid, name, matchCondition = item
            try:
                property = Path.PropertySegment(segment, match)
            except ValueError:
                self.assertFalse(valid, msg="Failed #{}".format(ctr + 1))
            else:
                self.assertTrue(valid, msg="Failed #{}".format(ctr + 1))
                self.assertEqual(property.name, name, msg="Failed #{}".format(ctr + 1))
                self.assertEqual(property.matchCondition, matchCondition, msg="Failed #{}".format(ctr + 1))


class TestParameterSegment(unittest.TestCase):

    test_data = (
        # Valid
        ("PARTSTAT", True, "PARTSTAT",),

        # Invalid
        ("", False, None,),
        ("PARTSTAT[]", False, None,),
        ("PARTSTAT[", False, None,),
        ("PARTSTAT[=NEEDS-ACTION]", False, None,),
    )

    def testParse(self):

        for ctr, item in enumerate(TestParameterSegment.test_data):
            segment, valid, name = item
            try:
                property = Path.ParameterSegment(segment)
            except ValueError:
                self.assertFalse(valid, msg="Failed #{}".format(ctr + 1))
            else:
                self.assertTrue(valid, msg="Failed #{}".format(ctr + 1))
                self.assertEqual(property.name, name, msg="Failed #{}".format(ctr + 1))
