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

from utils import set_difference

class PyCalendarRecurrenceSet(object):

    def __init__(self):
        self.mRrules = []
        self.mExrules = []
        self.mRdates = []
        self.mExdates = []
        self.mRperiods = []
        self.mExperiods = []

    def duplicate(self):
        other = PyCalendarRecurrenceSet()
        other.mRrules = [i.duplicate() for i in self.mRrules]
        other.mExrules = [i.duplicate() for i in self.mExrules]
        other.mRdates = [i.duplicate() for i in self.mRdates]
        other.mExdates = [i.duplicate() for i in self.mExdates]
        other.mRperiods = [i.duplicate() for i in self.mRperiods]
        other.mExperiods = [i.duplicate() for i in self.mExperiods]
        return other

    def hasRecurrence(self):
        return ((len(self.mRrules) != 0) or (len(self.mRdates) != 0) or (len(self.mRperiods) != 0)
                    or (len(self.mExrules) != 0) or (len(self.mExdates) != 0)
                    or (len(self.mExperiods) != 0))

    def equals(self, comp):
        # Look at RRULEs
        if not self.equalsRules(self.mRrules, comp.self.mRrules):
            return False

        # Look at EXRULEs
        if not self.equalsRules(self.mExrules, comp.self.mExrules):
            return False

        # Look at RDATEs
        if not self.equalsDates(self.mRdates, comp.self.mRdates):
            return False
        if not self.equalsPeriods(self.mRperiods, comp.self.mRperiods):
            return False

        # Look at EXDATEs
        if not self.equalsDates(self.mExdates, comp.self.mExdates):
            return False
        if not self.equalsPeriods(self.mExperiods, comp.self.mExperiods):
            return False

        # If we get here they match
        return True

    def equalsRules(self, rules1, rules2):
        # Check sizes first
        if len(rules1) != len(rules2):
            return False
        elif len(rules1) == 0:
            return True

        # Do sledge hammer O(n^2) approach as its not easy to sort these things
        # for a smarter test.
        # In most cases there will only be one rule anyway, so this should not
        # be too painful.

        temp2 = rules2[:]

        for r1 in rules1:
            found = False
            for r2 in temp2:
                if r1.equals(r2):
                    # Remove the one found so it is not tested again
                    temp2.remove(r2)
                    found = True
                    break

            if not found:
                return False

        return True

    def equalsDates(self, dates1, dates2):
        # Check sizes first
        if len(dates1) != len(dates2):
            return False
        elif len(dates1) == 0:
            return True

        # Copy each and sort for comparison
        dt1 = dates1[:]
        dt2 = dates2[:]

        dt1.sort(key=lambda x:x.getPosixTime())
        dt2.sort(key=lambda x:x.getPosixTime())

        return dt1.equal(dt2)

    def equalsPeriods(self, periods1, periods2):
        # Check sizes first
        if len(periods1) != len(periods2):
            return False
        elif len(periods1) == 0:
            return True

        # Copy each and sort for comparison
        p1 = periods1[:]
        p2 = periods2[:]

        p1.sort()
        p2.sort()

        return p1.equal(p2)

    def addRule(self, rule):
        self.mRrules.append(rule)

    def subtractRule(self, rule):
        self.mExrules.append(rule)

    def addDT(self, dt):
        self.mRdates.append(dt)

    def subtractDT(self, dt):
        self.mExdates.append(dt)

    def addPeriod(self, p):
        self.mRperiods.append(p)

    def subtractPeriod(self, p):
        self.mExperiods.append(p)

    def getRules(self):
        return self.mRrules

    def getExrules(self):
        return self.mExrules

    def getDates(self):
        return self.mRdates

    def getExdates(self):
        return self.mExdates

    def getPeriods(self):
        return self.mRperiods

    def getExperiods(self):
        return self.mExperiods

    def expand(self, start, range, items, float_offset=0):
        # Need to return whether the limit was applied or not
        limited = False

        # Now create list of items to include
        include = []

        # Always include the initial DTSTART if within the range
        if range.isDateWithinPeriod(start):
            include.append(start)
        else:
            limited = True

        # RRULES
        for iter in self.mRrules:
            if iter.expand(start, range, include, float_offset=float_offset):
                limited = True

        # RDATES
        for iter in self.mRdates:
            if range.isDateWithinPeriod(iter):
                include.append(iter)
            else:
                limited = True
        for iter in self.mRperiods:
            if range.isPeriodOverlap(iter):
                include.append(iter.getStart())
            else:
                limited = True

        # Make sure the list is unique
        include = [x for x in set(include)]
        include.sort(key=lambda x:x.getPosixTime())

        # Now create list of items to exclude
        exclude = []

        # EXRULES
        for iter in self.mExrules:
            iter.expand(start, range, exclude, float_offset=float_offset)

        # EXDATES
        for iter in self.mExdates:
            if range.isDateWithinPeriod(iter):
                exclude.append(iter)
        for iter in self.mExperiods:
            if range.isPeriodOverlap(iter):
                exclude.append(iter.getStart())

        # Make sure the list is unique
        exclude = [x for x in set(exclude)]
        exclude.sort(key=lambda x:x.getPosixTime())

        # Add difference between to the two sets (include - exclude) to the
        # results
        items.extend(set_difference(include, exclude))
        return limited

    def changed(self):
        # RRULES
        for iter in self.mRrules:
            iter.clear()

        # EXRULES
        for iter in self.mExrules:
            iter.clear()

    def excludeFutureRecurrence(self, exclude):
        # Adjust RRULES to end before start
        for iter in self.mRrules:
            iter.excludeFutureRecurrence(exclude)

        # Remove RDATES on or after start
        self.mRdates.removeOnOrAfter(exclude)
        for iter in self.mRperiods:
            if iter > exclude:
                self.mRperiods.remove(iter)

    # UI operations
    def isSimpleUI(self):
        # Right now the Event dialog only handles a single RRULE (but we allow
        # any number of EXDATES as deleted
        # instances will appear as EXDATES)
        if ((len(self.mRrules) > 1) or (len(self.mExrules) > 0)
                or (len(self.mRdates) > 0) or (len(self.mRperiods) > 0)):
            return False

        # Also, check the rule iteself
        elif len(self.mRrules) == 1:
            return self.mRrules.firstElement().isSimpleRule()
        else:
            return True

    def isAdvancedUI(self):
        # Right now the Event dialog only handles a single RRULE
        if ((len(self.mRrules) > 1) or (len(self.mExrules) > 0)
                or (len(self.mRdates) > 0) or (len(self.mRperiods) > 0)):
            return False

        # Also, check the rule iteself
        elif len(self.mRrules) == 1:
            return self.mRrules.firstElement().isAdvancedRule()
        else:
            return True

    def getUIRecurrence(self):
        if len(self.mRrules) == 1:
            return self.mRrules[0]
        else:
            return None

    def getUIDescription(self):
        # Check for anything
        if not self.hasRecurrence():
            return "No Recurrence"

        # Look for a single RRULE and return its descriptor
        if ((len(self.mRrules) == 1) and (len(self.mExrules) == 0) and (len(self.mRdates) == 0)
                and (len(self.mExdates) == 0) and (len(self.mRperiods) == 0)
                and (len(self.mExperiods) == 0)):
            return self.mRrules.firstElement().getUIDescription()

        # Indicate some form of complex recurrence
        return "Multiple recurrence rules, dates or exclusions"
