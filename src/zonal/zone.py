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

from pycalendar.datetime import PyCalendarDateTime
from pycalendar.vtimezone import PyCalendarVTimezone
from pycalendar.property import PyCalendarProperty
from pycalendar import definitions
from pycalendar.vtimezonestandard import PyCalendarVTimezoneStandard
from pycalendar.utcoffsetvalue import PyCalendarUTCOffsetValue
import utils
import rule

"""
Class that maintains a TZ data Zone.
"""

__all__ = (
    "Zone",
    "ZoneRule",
)

class Zone(object):
    """
    A tzdata Zone object containing a set of ZoneRules
    """

    def __init__(self):
        self.name = ""
        self.rules = []


    def __str__(self):
        return self.generate()


    def __eq__(self, other):
        return other and (
            self.name == other.name and
            self.rules == other.rules
        )


    def __ne__(self, other):
        return not self.__eq__(other)


    def parse(self, lines):
        """
        Parse the Zone lines from tzdata.

        @param lines: the lines to parse.
        @type lines: C{str}
        """

        # Parse one line at a time
        splitlines = lines.split("\n")

        # First line is special
        line = splitlines[0]
        splits = [x for x in line.expandtabs(1).split(" ") if len(x) > 0]
        self.name = splits[1]
        rule = ZoneRule(self)
        rule.parse(line, 0)
        self.rules.append(rule)
        for line in splitlines[1:]:
            if len(line) == 0:
                continue
            rule = ZoneRule(self)
            rule.parse(line, 2)
            if rule.gmtoff != "#":
                self.rules.append(rule)


    def generate(self):
        """
        Generate a partial Zone line.

        @return: a C{str} with the Rule.
        """

        lines = []
        for count, rule in enumerate(self.rules):
            if count == 0:
                items = (
                    "Zone " + self.name,
                    rule.generate(),
                )
            else:
                items = (
                    "",
                    "",
                    "",
                    rule.generate(),
                )
            lines.append("\t".join(items))
        return "\n".join(lines)


    def expand(self, rules, minYear, maxYear):
        """
        Expand this zone into a set of transitions.

        @param rules: parsed Rules for the tzdb
        @type rules: C{dict}
        @param minYear: starting year
        @type minYear: C{int}
        @param maxYear: ending year
        @type maxYear: C{int}

        @return: C{list} of C{tuple} for (
            transition date-time,
            offset to,
            offset from,
            associated rule,
        )
        """

        # Start at 1/1/1800 with the offset from the initial zone rule
        start = PyCalendarDateTime(year=1800, month=1, day=1, hours=0, minutes=0, seconds=0)
        start_offset = self.rules[0].getUTCOffset()
        start_stdoffset = self.rules[0].getUTCOffset()
        startdt = start.duplicate()

        # Now add each zone rules dates
        transitions = []
        lastUntilDateUTC = start.duplicate()
        last_offset = start_offset
        last_stdoffset = start_stdoffset
        first = True
        for zonerule in self.rules:
            last_offset, last_stdoffset = zonerule.expand(rules, transitions, lastUntilDateUTC, last_offset, last_stdoffset, maxYear)
            lastUntilDate = zonerule.getUntilDate()
            lastUntilDateUTC = lastUntilDate.getUTC(last_offset, last_stdoffset)

            # We typically don't care about the initial one
            if first and len(self.rules) > 1:
                transitions = []
                first = False

        # Sort the results by date
        transitions.sort(cmp=lambda x, y: x[0].compareDateTime(y[0]))

        # Now scan transitions looking for real changes and note those
        results = []
        last_transition = (startdt, start_offset, start_offset)
        for transition in transitions:
            dtutc, to_offset, zonerule, rule = transition
            dt = dtutc.duplicate()
            dt.offsetSeconds(last_transition[1])

            if dtutc.getYear() >= minYear:
                if dt > last_transition[0]:
                    results.append((dt, last_transition[1], to_offset, zonerule, rule))
                elif dt <= last_transition[0]:
                    if len(results):
                        results[-1] = ((results[-1][0], results[-1][1], to_offset, zonerule, None))
                    else:
                        results.append((last_transition[0], last_transition[1], last_transition[2], zonerule, None))
            last_transition = (dt, to_offset, last_transition[2], rule)

        return results


    def vtimezone(self, calendar, rules, minYear, maxYear):
        """
        Generate a VTIMEZONE for this Zone.

        @param calendar: the L{PyCalendar} object for the VCALENDAR in which the VTIMEZONE
            will be created.
        @param rules: the C{dict} containing the set of Rules currently defined.
        @param startYear: a C{int} containing the first year that should be present
            in the VTIMEZONE.
        @return: C{vtimezone} component.
        """

        # Get a VTIMEZONE component
        vtz = PyCalendarVTimezone(parent=calendar)

        # Add TZID property
        vtz.addProperty(PyCalendarProperty(definitions.cICalProperty_TZID, self.name))
        vtz.addProperty(PyCalendarProperty("X-LIC-LOCATION", self.name))

        transitions = self.expand(rules, minYear, maxYear)

        # Group rules
        lastZoneRule = None
        ruleorder = []
        rulemap = {}


        def _generateRuleData():
            # Generate VTIMEZONE component for last set of rules
            for rule in ruleorder:
                if rule:
                    # Accumulate rule portions with the same offset pairs
                    lastOffsetPair = (rulemap[rule][0][1], rulemap[rule][0][2],)
                    startIndex = 0
                    for index in xrange(len(rulemap[rule])):
                        offsetPair = (rulemap[rule][index][1], rulemap[rule][index][2],)
                        if offsetPair != lastOffsetPair:
                            rule.vtimezone(
                                vtz,
                                lastZoneRule,
                                rulemap[rule][startIndex][0],
                                rulemap[rule][index - 1][0],
                                rulemap[rule][startIndex][1],
                                rulemap[rule][startIndex][2],
                                index - startIndex,
                            )
                            lastOffsetPair = (rulemap[rule][index][1], rulemap[rule][index][2],)
                            startIndex = index

                    rule.vtimezone(
                        vtz,
                        lastZoneRule,
                        rulemap[rule][startIndex][0],
                        rulemap[rule][index][0],
                        rulemap[rule][startIndex][1],
                        rulemap[rule][startIndex][2],
                        len(rulemap[rule]),
                    )
                else:
                    lastZoneRule.vtimezone(
                        vtz,
                        lastZoneRule,
                        rulemap[rule][0][0],
                        rulemap[rule][-1][0],
                        rulemap[rule][0][1],
                        rulemap[rule][0][2],
                    )
            del ruleorder[:]
            rulemap.clear()

        for dt, offsetfrom, offsetto, zonerule, rule in transitions:

            # Check for change of rule - we ignore LMT's
            if zonerule.format != "LMT":
                if lastZoneRule and lastZoneRule != zonerule:
                    _generateRuleData()
                if rule not in ruleorder:
                    ruleorder.append(rule)
                rulemap.setdefault(rule, []).append((dt, offsetfrom, offsetto,))
            lastZoneRule = zonerule

        # Do left overs
        _generateRuleData()

        self._compressRDateComponents(vtz)

        vtz.finalise()
        return vtz


    def _compressRDateComponents(self, vtz):
        """
        Compress sub-components with RDATEs into a single component with multiple
        RDATEs assuming all other properties are the same.

        @param vtz: the VTIMEZONE object to compress
        @type vtz: L{PyCalendarVTimezone}
        """

        # Map the similar sub-components together
        similarMap = {}
        for item in vtz.mComponents:
            item.finalise()
            key = (
                item.getType(),
                item.getTZName(),
                item.getUTCOffset(),
                item.getUTCOffsetFrom(),
            )
            if item.hasProperty(definitions.cICalProperty_RDATE):
                similarMap.setdefault(key, []).append(item)

        # Merge similar
        for values in similarMap.itervalues():
            if len(values) > 1:
                mergeTo = values[0]
                for mergeFrom in values[1:]:
                    # Copy RDATE from to and remove from actual timezone
                    prop = mergeFrom.getProperties()[definitions.cICalProperty_RDATE][0]
                    mergeTo.addProperty(prop)
                    vtz.mComponents.remove(mergeFrom)



class ZoneRule(object):
    """
    A specific rule for a portion of a Zone
    """

    def __init__(self, zone):
        self.zone = zone
        self.gmtoff = 0
        self.rule = ""
        self.format = ""
        self.until = None


    def __str__(self):
        return self.generate()


    def __eq__(self, other):
        return other and (
            self.gmtoff == other.gmtoff and
            self.rule == other.rule and
            self.format == other.format and
            self.until == other.until
        )


    def __ne__(self, other):
        return not self.__eq__(other)


    def parse(self, line, offset):
        """
        Parse the Zone line from tzdata.

        @param line: a C{str} containing the line to parse.
        """

        splits = [x for x in line.expandtabs(1).split(" ") if len(x) > 0]
        assert len(splits) + offset >= 5, "Help: %s" % (line,)
        self.gmtoff = splits[2 - offset]
        self.rule = splits[3 - offset]
        self.format = splits[4 - offset]
        if len(splits) >= 6 - offset:
            self.until = " ".join(splits[5 - offset:])


    def generate(self):
        """
        Generate a partial Zone line.

        @return: a C{str} with the Rule.
        """
        items = (
            self.gmtoff,
            self.rule,
            self.format,
        )
        if self.until:
            items = items + (self.until,)
        return "\t".join(items)


    def getUntilDate(self):

        if hasattr(self, "_cached_until"):
            return self._cached_until

        year = 9999
        month = 12
        day = 1
        hours = 0
        minutes = 0
        seconds = 0
        mode = None
        if self.until and not self.until.startswith("#"):
            splits = self.until.split(" ")
            year = int(splits[0])
            month = 1
            day = 1
            hours = 0
            minutes = 0
            seconds = 0
            mode = None
            if len(splits) > 1 and not splits[1].startswith("#"):
                month = int(rule.Rule.MONTH_NAME_TO_POS[splits[1]])
                if len(splits) > 2 and not splits[2].startswith("#"):
                    if splits[2] == "lastSun":
                        dt = PyCalendarDateTime(year=year, month=month, day=1)
                        dt.setDayOfWeekInMonth(-1, PyCalendarDateTime.SUNDAY)
                        splits[2] = dt.getDay()
                    elif splits[2] == "lastSat":
                        dt = PyCalendarDateTime(year=year, month=month, day=1)
                        dt.setDayOfWeekInMonth(-1, PyCalendarDateTime.SATURDAY)
                        splits[2] = dt.getDay()
                    elif splits[2] == "Sun>=1":
                        dt = PyCalendarDateTime(year=year, month=month, day=1)
                        dt.setDayOfWeekInMonth(1, PyCalendarDateTime.SUNDAY)
                        splits[2] = dt.getDay()
                    day = int(splits[2])
                    if len(splits) > 3 and not splits[3].startswith("#"):
                        splits = splits[3].split(":")
                        hours = int(splits[0])
                        minutes = int(splits[1][:2])
                        if len(splits[1]) > 2:
                            mode = splits[1][2:]
                        else:
                            mode = None
                        if len(splits) > 2:
                            seconds = int(splits[2])

        dt = PyCalendarDateTime(year=year, month=month, day=day, hours=hours, minutes=minutes, seconds=seconds)
        self._cached_until = utils.DateTime(dt, mode)
        return self._cached_until


    def getUTCOffset(self):

        if hasattr(self, "_cached_utc_offset"):
            return self._cached_uutc_offset

        splits = self.gmtoff.split(":")

        hours = int(splits[0] if splits[0][0] != "-" else splits[0][1:])
        minutes = int(splits[1]) if len(splits) > 1 else 0
        seconds = int(splits[2]) if len(splits) > 2 else 0
        negative = splits[0][0] == "-"
        self._cached_uutc_offset = ((hours * 60) + minutes) * 60 + seconds
        if negative:
            self._cached_uutc_offset = -self._cached_uutc_offset
        return self._cached_uutc_offset


    def expand(self, rules, results, lastUntilUTC, lastOffset, lastStdOffset, maxYear):

        # Expand the rule
        assert self.rule == "-" or self.rule[0].isdigit() or self.rule in rules, "No rule '%s' found in cache. %s for %s" % (self.rule, self, self.zone,)
        if self.rule == "-" or self.rule[0].isdigit():
            return self.expand_norule(results, lastUntilUTC, maxYear)
        else:
            tempresults = []

            ruleset = rules[self.rule]
            ruleset.expand(tempresults, self, maxYear)

            # Sort the results by date
            tempresults.sort(cmp=lambda x, y: x[0].compareDateTime(y[0]))

            found_one = False
            found_start = False
            last_offset = lastOffset
            last_stdoffset = lastStdOffset
            finalUntil = self.getUntilDate()
            for dt, to_offset, rule in tempresults:
                dtutc = dt.getUTC(last_offset, last_stdoffset)
                if dtutc >= lastUntilUTC:
                    if not found_start and dtutc != lastUntilUTC:
                        # Insert a start item
                        if not found_one:
                            last_offset = self.getUTCOffset()
                            last_stdoffset = self.getUTCOffset()
                            dtutc = dt.getUTC(last_offset, last_stdoffset)
                        results.append((lastUntilUTC, last_offset, self, None))
                    found_start = True

                    if dtutc >= finalUntil.getUTC(last_offset, last_stdoffset):
                        break

                    results.append((dtutc, to_offset, self, rule))

                last_offset = to_offset
                last_stdoffset = self.getUTCOffset()
                found_one = True

            if found_start == 0:
                results.append((lastUntilUTC, last_offset, self, None))

            return last_offset, last_stdoffset


    def expand_norule(self, results, lastUntil, maxYear):
        to_offset = 0
        if self.rule[0].isdigit():
            splits = self.rule.split(":")
            to_offset = 60 * 60 * int(splits[0])
            if len(splits) > 1:
                to_offset += 60 * int(splits[1])

        # Always add a transition for the start of this rule
        results.append((lastUntil, self.getUTCOffset() + to_offset, self, None))
        return (self.getUTCOffset() + to_offset, self.getUTCOffset())


    def vtimezone(self, vtz, zonerule, start, end, offsetfrom, offsetto):

        # Determine type of component based on offset
        comp = PyCalendarVTimezoneStandard(parent=vtz)

        # Do offsets
        tzoffsetfrom = PyCalendarUTCOffsetValue(offsetfrom)
        tzoffsetto = PyCalendarUTCOffsetValue(offsetto)

        comp.addProperty(PyCalendarProperty(definitions.cICalProperty_TZOFFSETFROM, tzoffsetfrom))
        comp.addProperty(PyCalendarProperty(definitions.cICalProperty_TZOFFSETTO, tzoffsetto))

        # Do TZNAME
        if self.format.find("%") != -1:
            tzname = self.format % ("S",)
        else:
            tzname = self.format
        comp.addProperty(PyCalendarProperty(definitions.cICalProperty_TZNAME, tzname))

        # Do DTSTART
        comp.addProperty(PyCalendarProperty(definitions.cICalProperty_DTSTART, start))

        # Recurrence
        comp.addProperty(PyCalendarProperty(definitions.cICalProperty_RDATE, start))

        comp.finalise()
        vtz.addComponent(comp)

if __name__ == '__main__':
    rulesdef = """Rule\tUS\t1918\t1919\t-\tMar\tlastSun\t2:00\t1:00\tD
Rule\tUS\t1918\t1919\t-\tOct\tlastSun\t2:00\t0\tS
Rule\tUS\t1942\tonly\t-\tFeb\t9\t2:00\t1:00\tW # War
Rule\tUS\t1945\tonly\t-\tAug\t14\t23:00u\t1:00\tP # Peace
Rule\tUS\t1945\tonly\t-\tSep\t30\t2:00\t0\tS
Rule\tUS\t1967\t2006\t-\tOct\tlastSun\t2:00\t0\tS
Rule\tUS\t1967\t1973\t-\tApr\tlastSun\t2:00\t1:00\tD
Rule\tUS\t1974\tonly\t-\tJan\t6\t2:00\t1:00\tD
Rule\tUS\t1975\tonly\t-\tFeb\t23\t2:00\t1:00\tD
Rule\tUS\t1976\t1986\t-\tApr\tlastSun\t2:00\t1:00\tD
Rule\tUS\t1987\t2006\t-\tApr\tSun>=1\t2:00\t1:00\tD
Rule\tUS\t2007\tmax\t-\tMar\tSun>=8\t2:00\t1:00\tD
Rule\tUS\t2007\tmax\t-\tNov\tSun>=1\t2:00\t0\tS"""
    rules = {}
    import rule
    ruleset = rule.RuleSet()
    ruleset.parse(rulesdef)
    rules[ruleset.name] = ruleset

    zonedef = """Zone America/New_York -4:56:02\t-\tLMT\t1883 Nov 18 12:03:58
\t\t\t-5:00\tUS\tE%sT\t1920
\t\t\t-5:00\tNYC\tE%sT\t1942
\t\t\t-5:00\tUS\tE%sT\t1946
\t\t\t-5:00\tNYC\tE%sT\t1967
\t\t\t-5:00\tUS\tE%sT"""
    zone = Zone()
    zone.parse(zonedef)
