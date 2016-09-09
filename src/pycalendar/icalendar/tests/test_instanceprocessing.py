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

from difflib import unified_diff
from pycalendar.icalendar.calendar import Calendar
from pycalendar.icalendar.instanceprocessing import InstanceExpander, InstanceCompactor
import json
import os
import unittest


dataValid = [
    {
        "title": "Remove one component from the instance",
        "compact": """BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:1234
DTSTART;VALUE=DATE:20160902
DURATION:PT1H
LOCATION:My office
RRULE:FREQ=DAILY
SUMMARY:Master component
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
BEGIN:VINSTANCE
RECURRENCE-ID;VALUE=DATE:20160903
INSTANCE-DELETE:/VALARM[UID=4567]
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:1234
DTSTART;VALUE=DATE:20160902
DURATION:PT1H
LOCATION:My office
RRULE:FREQ=DAILY
SUMMARY:Master component
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
BEGIN:VEVENT
UID:1234
RECURRENCE-ID;VALUE=DATE:20160903
DTSTART;VALUE=DATE:20160903
DURATION:PT1H
LOCATION:My office
SUMMARY:Master component
BEGIN:VALARM
UID:89AB
ACTION:DISPLAY
TRIGGER:-PT5M
DESCRIPTION:Time to leave (5 mins)
END:VALARM
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Remove one property from the instance",
        "compact": """BEGIN:VCALENDAR
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
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:1234
DTSTART;VALUE=DATE:20160902
DURATION:PT1H
LOCATION:My office
RRULE:FREQ=DAILY
SUMMARY:Master component
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID;VALUE=DATE:20160903
DTSTART;VALUE=DATE:20160903
DURATION:PT1H
SUMMARY:Master component
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Add an alarm to the instance",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:My office
RRULE:FREQ=DAILY
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
BEGIN:VALARM
UID:4567
ACTION:DISPLAY
TRIGGER:-PT30M
DESCRIPTION:Time to leave
END:VALARM
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:My office
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID:20160903T120000Z
DTSTART:20160903T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:My office
BEGIN:VALARM
UID:4567
ACTION:DISPLAY
TRIGGER:-PT30M
DESCRIPTION:Time to leave
END:VALARM
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Update an alarm in the instance",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:My office
RRULE:FREQ=DAILY
BEGIN:VALARM
UID:4567
ACTION:DISPLAY
TRIGGER:-PT30M
DESCRIPTION:Time to leave (30 mins)
END:VALARM
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
BEGIN:VALARM
UID:4567
ACTION:DISPLAY
TRIGGER:-PT5M
DESCRIPTION:Time to leave (5 mins)
END:VALARM
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:My office
RRULE:FREQ=DAILY
BEGIN:VALARM
UID:4567
ACTION:DISPLAY
TRIGGER:-PT30M
DESCRIPTION:Time to leave (30 mins)
END:VALARM
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID:20160903T120000Z
DTSTART:20160903T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:My office
BEGIN:VALARM
UID:4567
ACTION:DISPLAY
TRIGGER:-PT5M
DESCRIPTION:Time to leave (5 mins)
END:VALARM
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Add a singleton property to the instance",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
SUMMARY:Master component
RRULE:FREQ=DAILY
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
LOCATION:My office
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
SUMMARY:Master component
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID:20160903T120000Z
DTSTART:20160903T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:My office
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Update a singleton property in the instance",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
LOCATION:Your office
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID:20160903T120000Z
DTSTART:20160903T120000Z
DURATION:PT1H
SUMMARY:Master component
LOCATION:Your office
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Add a multi-occurring property to the instance",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
CATEGORIES:meeting
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
CATEGORIES;INSTANCE-ACTION=CREATE:one-on-one
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
CATEGORIES:meeting
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID:20160903T120000Z
DTSTART:20160903T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES:one-on-one
LOCATION:My office
SUMMARY:Master component
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Update a multi-occurring property by value in the instance",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES:one-on-one
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
CATEGORIES;INSTANCE-ACTION=BYVALUE;X-PARAM=0:one-on-one
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES:one-on-one
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID:20160903T120000Z
DTSTART:20160903T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES;X-PARAM=0:one-on-one
LOCATION:My office
SUMMARY:Master component
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Update a multi-occurring property by parameter in the instance",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES;X-PARAM=0:one-on-one
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
CATEGORIES;INSTANCE-ACTION="BYPARAM@X-PARAM=0":just-you-and-me
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
        "expanded": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES;X-PARAM=0:one-on-one
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:1234
RECURRENCE-ID:20160903T120000Z
DTSTART:20160903T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES:just-you-and-me
LOCATION:My office
SUMMARY:Master component
END:VEVENT
END:VCALENDAR
""",
    },
]

dataInvalid = [
    {
        "title": "Invalid delete path",
        "compact": """BEGIN:VCALENDAR
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
INSTANCE-DELETE:#LOCATION;LANGUAGE
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
    },
    {
        "title": "Invalid instance action parameter",
        "compact": """BEGIN:VCALENDAR
PRODID:test
VERSION:2.0
BEGIN:VEVENT
UID:1234
DTSTART:20160902T120000Z
DURATION:PT1H
CATEGORIES:meeting
CATEGORIES;X-PARAM=0:one-on-one
LOCATION:My office
SUMMARY:Master component
RRULE:FREQ=DAILY
BEGIN:VINSTANCE
RECURRENCE-ID:20160903T120000Z
CATEGORIES;INSTANCE-ACTION=FOO:just-you-and-me
END:VINSTANCE
END:VEVENT
END:VCALENDAR
""",
    },
]


class TestInstanceExpand(unittest.TestCase):

    def test_expand(self):
        """
        Test that instance expansion works.
        """

        for ctr, items in enumerate(dataValid):
            compact = Calendar.parseText(items["compact"])
            expanded = Calendar.parseText(items["expanded"])
            try:
                InstanceExpander.expand(compact)
            except Exception as e:
                self.fail("Failed test #{}: {}\n{}".format(ctr + 1, items["title"], str(e)))
            else:
                self.assertEqual(
                    str(compact),
                    str(expanded),
                    msg="Failed test #{}: {}\n{}".format(
                        ctr + 1,
                        items["title"],
                        "\n".join(unified_diff(str(compact).splitlines(), str(expanded).splitlines())),
                    ),
                )

    def test_invalid(self):
        """
        Test that invalid patch data correctly fail to parse.
        """

        for ctr, items in enumerate(dataInvalid):
            compact = Calendar.parseText(items["compact"])
            try:
                InstanceExpander.expand(compact)
            except Exception:
                pass
            else:
                self.fail("Failed test #{} - no exception raised: {}".format(ctr + 1, items["title"]))


class TestInstanceCompact(unittest.TestCase):

    def test_compact(self):
        """
        Test that instance expansion works.
        """

        for ctr, items in enumerate(dataValid):
            if "BYPARAM" in items["compact"]:
                continue
            compact = Calendar.parseText(items["compact"])
            expanded = Calendar.parseText(items["expanded"])
            try:
                InstanceCompactor.compact(expanded)
            except Exception as e:
                self.fail("Failed test #{}: {}\n{}".format(ctr + 1, items["title"], str(e)))
            else:
                self.assertEqual(
                    str(expanded),
                    str(compact),
                    msg="Failed test #{}: {}\n{}".format(
                        ctr + 1,
                        items["title"],
                        "\n".join(unified_diff(str(expanded).splitlines(), str(compact).splitlines())),
                    ),
                )

if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), "vinstance_examples.json"), "w") as f:
        f.write(json.dumps(dataValid, indent=2))
    print("Updated vinstance_examples.json")

    with open(os.path.join(os.path.dirname(__file__), "vinstance_invalid_examples.json"), "w") as f:
        f.write(json.dumps(dataInvalid, indent=2))
    print("Updated vinstance_invalid_examples.json")
