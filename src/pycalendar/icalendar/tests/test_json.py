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
import difflib
import unittest

class TestJSON(unittest.TestCase):

    data = (
                (
"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//Example Inc.//Example Calendar//EN
VERSION:2.0
BEGIN:VEVENT
DTSTAMP:20080205T191224Z
DTSTART;VALUE=DATE:20081006
SUMMARY:Planning meeting
UID:4088E990AD89CB3DBB484909
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""[
  "vcalendar",
  [
    [
      "version",
      {},
      "text",
      "2.0"
    ],
    [
      "calscale",
      {},
      "text",
      "GREGORIAN"
    ],
    [
      "prodid",
      {},
      "text",
      "-//Example Inc.//Example Calendar//EN"
    ]
  ],
  [
    [
      "vevent",
      [
        [
          "uid",
          {},
          "text",
          "4088E990AD89CB3DBB484909"
        ],
        [
          "dtstart",
          {},
          "date",
          "2008-10-06"
        ],
        [
          "dtstamp",
          {},
          "date-time",
          "2008-02-05T19:12:24Z"
        ],
        [
          "summary",
          {},
          "text",
          "Planning meeting"
        ]
      ],
      []
    ]
  ]
]""",
                ),
                (
"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//Example Client//EN
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
DTSTAMP:20060206T001121Z
DTSTART;TZID=US/Eastern:20060102T120000
DURATION:PT1H
GEO:-123.45;67.89
RRULE:FREQ=DAILY;COUNT=5
RDATE;TZID=US/Eastern;VALUE=PERIOD:20060102T150000/PT2H
SUMMARY:Event #2
DESCRIPTION:We are having a meeting all this week at 12 pm fo
 r one hour\\, with an additional meeting on the first day 2 h
 ours long.\\nPlease bring your own lunch for the 12 pm meetin
 gs.
UID:00959BC664CA650E933C892C@example.com
END:VEVENT
BEGIN:VEVENT
DTSTAMP:20060206T001121Z
DTSTART;TZID=US/Eastern:20060104T140000
DURATION:PT1H
RECURRENCE-ID;TZID=US/Eastern:20060104T120000
SUMMARY:Event #2 bis
UID:00959BC664CA650E933C892C@example.com
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),

"""[
  "vcalendar",
  [
    [
      "version",
      {},
      "text",
      "2.0"
    ],
    [
      "prodid",
      {},
      "text",
      "-//Example Corp.//Example Client//EN"
    ]
  ],
  [
    [
      "vtimezone",
      [
        [
          "tzid",
          {},
          "text",
          "US/Eastern"
        ],
        [
          "last-modified",
          {},
          "date-time",
          "2004-01-10T03:28:45Z"
        ]
      ],
      [
        [
          "daylight",
          [
            [
              "dtstart",
              {},
              "date-time",
              "2000-04-04T02:00:00"
            ],
            [
              "rrule",
              {},
              "recur",
              {
                "bymonth":[
                  4
                ],
                "freq":"YEARLY",
                "byday":[
                  "1SU"
                ]
              }
            ],
            [
              "tzname",
              {},
              "text",
              "EDT"
            ],
            [
              "tzoffsetfrom",
              {},
              "utc-offset",
              "-05:00"
            ],
            [
              "tzoffsetto",
              {},
              "utc-offset",
              "-04:00"
            ]
          ],
          []
        ],
        [
          "standard",
          [
            [
              "dtstart",
              {},
              "date-time",
              "2000-10-26T02:00:00"
            ],
            [
              "rrule",
              {},
              "recur",
              {
                "bymonth":[
                  10
                ],
                "freq":"YEARLY",
                "byday":[
                  "-1SU"
                ]
              }
            ],
            [
              "tzname",
              {},
              "text",
              "EST"
            ],
            [
              "tzoffsetfrom",
              {},
              "utc-offset",
              "-04:00"
            ],
            [
              "tzoffsetto",
              {},
              "utc-offset",
              "-05:00"
            ]
          ],
          []
        ]
      ]
    ],
    [
      "vevent",
      [
        [
          "uid",
          {},
          "text",
          "00959BC664CA650E933C892C@example.com"
        ],
        [
          "dtstart",
          {
            "tzid":"US/Eastern"
          },
          "date-time",
          "2006-01-02T12:00:00"
        ],
        [
          "duration",
          {},
          "duration",
          "PT1H"
        ],
        [
          "description",
          {},
          "text",
          "We are having a meeting all this week at 12 pm for one hour, with an additional meeting on the first day 2 hours long.\\nPlease bring your own lunch for the 12 pm meetings."
        ],
        [
          "dtstamp",
          {},
          "date-time",
          "2006-02-06T00:11:21Z"
        ],
        [
          "geo",
          {},
          "float",
          [
            -123.45,
            67.89
          ]
        ],
        [
          "rdate",
          {
            "tzid":"US/Eastern"
          },
          "period",
          [
            "2006-01-02T15:00:00",
            "PT2H"
          ]
        ],
        [
          "rrule",
          {},
          "recur",
          {
            "count":5,
            "freq":"DAILY"
          }
        ],
        [
          "summary",
          {},
          "text",
          "Event #2"
        ]
      ],
      []
    ],
    [
      "vevent",
      [
        [
          "uid",
          {},
          "text",
          "00959BC664CA650E933C892C@example.com"
        ],
        [
          "recurrence-id",
          {
            "tzid":"US/Eastern"
          },
          "date-time",
          "2006-01-04T12:00:00"
        ],
        [
          "dtstart",
          {
            "tzid":"US/Eastern"
          },
          "date-time",
          "2006-01-04T14:00:00"
        ],
        [
          "duration",
          {},
          "duration",
          "PT1H"
        ],
        [
          "dtstamp",
          {},
          "date-time",
          "2006-02-06T00:11:21Z"
        ],
        [
          "summary",
          {},
          "text",
          "Event #2 bis"
        ]
      ],
      []
    ]
  ]
]""",
            ),
        )

    def testGenerateJSON(self):

        def _doRoundtrip(caldata, resultdata):
            test1 = resultdata

            cal = Calendar.parseText(caldata)

            test2 = cal.getTextJSON()
            self.assertEqual(
                test1,
                test2,
                "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
            )

        for item1, item2 in self.data:
            _doRoundtrip(item1, item2)


    def testParseJSON(self):

        def _doRoundtrip(caldata, jcaldata):
            cal1 = Calendar.parseText(caldata)
            test1 = cal1.getText()

            cal2 = Calendar.parseJSONText(jcaldata)
            test2 = cal2.getText()

            self.assertEqual(
                test1,
                test2,
                "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
            )

        for item1, item2 in self.data:
            _doRoundtrip(item1, item2)


    def testjCalExample1(self):

        jcaldata = """["vcalendar",
  [
    ["calscale", {}, "text", "GREGORIAN"],
    ["prodid", {}, "text", "-//Example Inc.//Example Calendar//EN"],
    ["version", {}, "text", "2.0"]
  ],
  [
    ["vevent",
      [
        ["dtstamp", {}, "date-time", "2008-02-05T19:12:24Z"],
        ["dtstart", {}, "date", "2008-10-06"],
        ["summary", {}, "text", "Planning meeting"],
        ["uid", {}, "text", "4088E990AD89CB3DBB484909"]
      ],
      []
    ]
  ]
]
"""

        icaldata = """BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//Example Inc.//Example Calendar//EN
VERSION:2.0
BEGIN:VEVENT
DTSTAMP:20080205T191224Z
DTSTART;VALUE=DATE:20081006
SUMMARY:Planning meeting
UID:4088E990AD89CB3DBB484909
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")

        cal1 = Calendar.parseText(icaldata)
        test1 = cal1.getText()

        cal2 = Calendar.parseJSONText(jcaldata)
        test2 = cal2.getText()

        self.assertEqual(
            test1,
            test2,
            "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
        )


    def testjCalExample2(self):

        jcaldata = """["vcalendar",
  [
    ["prodid", {}, "text", "-//Example Corp.//Example Client//EN"],
    ["version", {}, "text", "2.0"]
  ],
  [
    ["vtimezone",
      [
        ["last-modified", {}, "date-time", "2004-01-10T03:28:45Z"],
        ["tzid", {}, "text", "US/Eastern"]
      ],
      [
        ["daylight",
          [
            ["dtstart", {}, "date-time", "2000-04-04T02:00:00"],
            ["rrule",
              {},
              "recur",
              {
                "freq": "YEARLY",
                "byday": "1SU",
                "bymonth": 4
              }
            ],
            ["tzname", {}, "text", "EDT"],
            ["tzoffsetfrom", {}, "utc-offset", "-05:00"],
            ["tzoffsetto", {}, "utc-offset", "-04:00"]
          ],
          []
        ],
        ["standard",
          [
            ["dtstart", {}, "date-time", "2000-10-26T02:00:00"],
            ["rrule",
              {},
              "recur",
              {
                "freq": "YEARLY",
                "byday": "-1SU",
                "bymonth": 10
              }
            ],
            ["tzname", {}, "text", "EST"],
            ["tzoffsetfrom", {}, "utc-offset", "-04:00"],
            ["tzoffsetto", {}, "utc-offset", "-05:00"]
          ],
          []
        ]
      ]
    ],
    ["vevent",
      [
        ["dtstamp", {}, "date-time", "2006-02-06T00:11:21Z"],
        ["dtstart",
          { "tzid": "US/Eastern" },
          "date-time",
          "2006-01-02T12:00:00"
        ],
        ["duration", {}, "duration", "PT1H"],
        ["rrule", {}, "recur", { "freq": "DAILY", "count": 5 } ],
        ["rdate",
          { "tzid": "US/Eastern" },
          "period",
          ["2006-01-02T15:00:00", "PT2H"]
        ],
        ["summary", {}, "text", "Event #2"],
        ["description",
         {},
         "text",
         "We are having a meeting all this week at 12 pm for one hour, with an additional meeting on the first day 2 hours long.\\nPlease bring your own lunch for the 12 pm meetings."
        ],
        ["uid", {}, "text", "00959BC664CA650E933C892C@example.com"]
      ],
      []
    ],
    ["vevent",
      [
        ["dtstamp", {}, "date-time", "2006-02-06T00:11:21Z"],
        ["dtstart",
          { "tzid": "US/Eastern" },
          "date-time",
          "2006-01-04T14:00:00"
        ],
        ["duration", {}, "duration", "PT1H"],
        ["recurrence-id",
          { "tzid": "US/Eastern" },
          "date-time",
          "2006-01-04T12:00:00"
        ],
        ["summary", {}, "text", "Event #2 bis"],
        ["uid", {}, "text", "00959BC664CA650E933C892C@example.com"]
      ],
      []
    ]
  ]
]
"""

        icaldata = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//Example Client//EN
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
DTSTAMP:20060206T001121Z
DTSTART;TZID=US/Eastern:20060102T120000
DURATION:PT1H
RRULE:FREQ=DAILY;COUNT=5
RDATE;TZID=US/Eastern;VALUE=PERIOD:20060102T150000/PT2H
SUMMARY:Event #2
DESCRIPTION:We are having a meeting all this week at 12 pm fo
 r one hour\\, with an additional meeting on the first day 2 h
 ours long.\\nPlease bring your own lunch for the 12 pm meetin
 gs.
UID:00959BC664CA650E933C892C@example.com
END:VEVENT
BEGIN:VEVENT
DTSTAMP:20060206T001121Z
DTSTART;TZID=US/Eastern:20060104T140000
DURATION:PT1H
RECURRENCE-ID;TZID=US/Eastern:20060104T120000
SUMMARY:Event #2 bis
UID:00959BC664CA650E933C892C@example.com
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n")

        cal1 = Calendar.parseText(icaldata)
        test1 = cal1.getText()

        cal2 = Calendar.parseJSONText(jcaldata)
        test2 = cal2.getText()

        self.assertEqual(
            test1,
            test2,
            "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
        )
