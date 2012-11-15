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
from zonal.rule import Rule, RuleSet
from pycalendar.datetime import PyCalendarDateTime

class TestRule(unittest.TestCase):

    def test_parse(self):
        data = (
            "Rule\tGuat\t2006\tonly\t-\tOct\t1\t0:00\t0\tS",
            "Rule\tAlgeria\t1916\t1919\t-\tOct\tSun>=1\t23:00s\t0\t-",
            "Rule\tEgypt\t1945\tonly\t-\tApr\t16\t0:00\t1:00\tS",
            "Rule\tGhana\t1936\t1942\t-\tSep\t1\t0:00\t0:20\tGHST",
        )

        for ruletext in data:
            ruleitem = Rule()
            ruleitem.parse(ruletext)

            self.assertEqual(str(ruleitem), ruletext)


    def test_datetimeforyear(self):
        data = (
            ("Rule\tGuat\t2006\tonly\t-\tOct\t1\t0:00\t0\tS", 2006, PyCalendarDateTime(2006, 10, 1, 0, 0, 0), ""),
            ("Rule\tAlgeria\t1916\t1919\t-\tOct\tSun>=1\t23:00s\t0\t-", 1916, PyCalendarDateTime(1916, 10, 1, 23, 0, 0), "s"),
            ("Rule\tGhana\t1936\t1942\t-\tSep\t1\t0:00\t0:20\tGHST", 1937, PyCalendarDateTime(1937, 9, 1, 0, 0, 0), ""),
        )

        for ruletext, year, dt, special in data:
            ruleitem = Rule()
            ruleitem.parse(ruletext)

            self.assertEqual(ruleitem.datetimeForYear(year), (dt, special))


    def test_getoffset(self):
        data = (
            ("Rule\tGuat\t2006\tonly\t-\tOct\t1\t0:00\t0\tS", 0),
            ("Rule\tEgypt\t1945\tonly\t-\tApr\t16\t0:00\t1:00\tS", 60 * 60),
            ("Rule\tGhana\t1936\t1942\t-\tSep\t1\t0:00\t0:20\tGHST", 20 * 60),
        )

        for ruletext, offset in data:
            ruleitem = Rule()
            ruleitem.parse(ruletext)

            self.assertEqual(ruleitem.getOffset(), offset)



class TestRuleSet(unittest.TestCase):

    def test_parse(self):
        data = """Rule\tUS\t1918\t1919\t-\tMar\tlastSun\t2:00\t1:00\tD
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

        ruleset = RuleSet()
        ruleset.parse(data)

        self.assertEqual(str(ruleset), data)
