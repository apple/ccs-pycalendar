##
#    Copyright (c) 2007-2012 Cyrus Daboo. All rights reserved.
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
from zonal.zone import Zone
from zonal.rule import RuleSet
from pycalendar.calendar import PyCalendar

class TestZone(unittest.TestCase):

    def test_parse(self):
        zonedef = """Zone America/New_York\t-4:56:02\t-\tLMT\t1883 Nov 18 12:03:58
\t\t\t-5:00\tUS\tE%sT\t1920
\t\t\t-5:00\tNYC\tE%sT\t1942
\t\t\t-5:00\tUS\tE%sT\t1946
\t\t\t-5:00\tNYC\tE%sT\t1967
\t\t\t-5:00\tUS\tE%sT"""
        zone = Zone()
        zone.parse(zonedef)

        self.assertEqual(str(zone), zonedef)


    def test_vtimezone(self):

        zonedef = """Zone America/New_York\t-4:56:02\t-\tLMT\t1883 Nov 18 12:03:58
\t\t\t-5:00\tUS\tE%sT"""
        rules = """Rule\tUS\t1918\t1919\t-\tMar\tlastSun\t2:00\t1:00\tD
Rule\tUS\t1918\t1919\t-\tOct\tlastSun\t2:00\t0\tS
Rule\tUS\t1942\tonly\t-\tFeb\t9\t2:00\t1:00\tW
Rule\tUS\t1945\tonly\t-\tAug\t14\t23:00u\t1:00\tP
Rule\tUS\t1945\tonly\t-\tSep\t30\t2:00\t0\tS
Rule\tUS\t1967\t2006\t-\tOct\tlastSun\t2:00\t0\tS
Rule\tUS\t1967\t1973\t-\tApr\tlastSun\t2:00\t1:00\tD
Rule\tUS\t1974\tonly\t-\tJan\t6\t2:00\t1:00\tD
Rule\tUS\t1975\tonly\t-\tFeb\t23\t2:00\t1:00\tD
Rule\tUS\t1976\t1986\t-\tApr\tlastSun\t2:00\t1:00\tD
Rule\tUS\t1987\t2006\t-\tApr\tSun>=1\t2:00\t1:00\tD
Rule\tUS\t2007\tmax\t-\tMar\tSun>=8\t2:00\t1:00\tD
Rule\tUS\t2007\tmax\t-\tNov\tSun>=1\t2:00\t0\tS"""
        result = """BEGIN:VTIMEZONE
TZID:America/New_York
X-LIC-LOCATION:America/New_York
BEGIN:DAYLIGHT
DTSTART:20060402T020000
RDATE:20060402T020000
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20061029T020000
RDATE:20061029T020000
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:20070311T020000
RRULE:FREQ=YEARLY;BYDAY=2SU;BYMONTH=3
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20071104T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=11
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
""".replace("\n", "\r\n")

        zone = Zone()
        zone.parse(zonedef)

        ruleset = RuleSet()
        ruleset.parse(rules)
        rules = {ruleset.name: ruleset}

        cal = PyCalendar()
        vtz = zone.vtimezone(cal, rules, 2006, 2011)

        self.assertEqual(str(vtz), result)
