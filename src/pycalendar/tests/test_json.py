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

class TestJSON(unittest.TestCase):
    
    data = (
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
  {
    "type": "vcalendar", 
    "properties": {
      "version": {
        "text": "2.0"
      }, 
      "prodid": {
        "text": "-//Example Corp.//Example Client//EN"
      }
    }, 
    "components": [
      {
        "type": "vtimezone", 
        "properties": {
          "tzid": {
            "text": "US/Eastern"
          }, 
          "last-modified": {
            "date-time": "2004-01-10T03:28:45Z"
          }
        }, 
        "components": [
          {
            "type": "daylight", 
            "properties": {
              "tzoffsetto": {
                "utc-offset": "-04:00"
              }, 
              "dtstart": {
                "date-time": "2000-04-04T02:00:00"
              }, 
              "rrule": {
                "recur": {
                  "bymonth": [
                    4
                  ], 
                  "freq": "YEARLY", 
                  "byday": [
                    "1SU"
                  ]
                }
              }, 
              "tzoffsetfrom": {
                "utc-offset": "-05:00"
              }, 
              "tzname": {
                "text": "EDT"
              }
            }
          }, 
          {
            "type": "standard", 
            "properties": {
              "tzoffsetto": {
                "utc-offset": "-05:00"
              }, 
              "dtstart": {
                "date-time": "2000-10-26T02:00:00"
              }, 
              "rrule": {
                "recur": {
                  "bymonth": [
                    10
                  ], 
                  "freq": "YEARLY", 
                  "byday": [
                    "-1SU"
                  ]
                }
              }, 
              "tzoffsetfrom": {
                "utc-offset": "-04:00"
              }, 
              "tzname": {
                "text": "EST"
              }
            }
          }
        ]
      }, 
      {
        "type": "vevent", 
        "properties": {
          "dtstamp": {
            "date-time": "2006-02-06T00:11:21Z"
          }, 
          "uid": {
            "text": "00959BC664CA650E933C892C@example.com"
          }, 
          "summary": {
            "text": "Event #2"
          }, 
          "rdate": {
            "period": [
              {
                "duration": "PT2H", 
                "start": "2006-01-02T15:00:00"
              }
            ], 
            "parameters": {
              "tzid": "US/Eastern"
            }
          }, 
          "rrule": {
            "recur": {
              "count": 5, 
              "freq": "DAILY"
            }
          }, 
          "duration": {
            "duration": "PT1H"
          }, 
          "dtstart": {
            "parameters": {
              "tzid": "US/Eastern"
            }, 
            "date-time": "2006-01-02T12:00:00"
          }, 
          "description": {
            "text": "We are having a meeting all this week at 12 pm for one hour, with an additional meeting on the first day 2 hours long.\\nPlease bring your own lunch for the 12 pm meetings."
          }
        }
      }, 
      {
        "type": "vevent", 
        "properties": {
          "dtstamp": {
            "date-time": "2006-02-06T00:11:21Z"
          }, 
          "uid": {
            "text": "00959BC664CA650E933C892C@example.com"
          }, 
          "recurrence-id": {
            "parameters": {
              "tzid": "US/Eastern"
            }, 
            "date-time": "2006-01-04T12:00:00"
          }, 
          "summary": {
            "text": "Event #2 bis"
          }, 
          "duration": {
            "duration": "PT1H"
          }, 
          "dtstart": {
            "parameters": {
              "tzid": "US/Eastern"
            }, 
            "date-time": "2006-01-04T14:00:00"
          }
        }
      }
    ]
  }
]""",
                ),
)

    def testGenerateJSON(self):

        def _doRoundtrip(caldata, resultdata=None):
            test1 = resultdata if resultdata is not None else caldata

            cal = PyCalendar()
            cal.parse(StringIO.StringIO(caldata))
            
            test2 = cal.getTextJSON()
            
            self.assertEqual(
                test1,
                test2,
                "\n".join(difflib.unified_diff(str(test1).splitlines(), test2.splitlines()))
            )

        for item1, item2 in self.data:
            _doRoundtrip(item1, item2)

