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

from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS

class VTimezone(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_TZID,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_LAST_MODIFIED,
        definitions.cICalProperty_TZURL,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    UTCOFFSET_CACHE_MAX_ENTRIES = 100000

    sortSubComponents = False

    def __init__(self, parent=None):
        super(VTimezone, self).__init__(parent=parent)
        self.mID = ""
        self.mUTCOffsetSortKey = None
        self.mCachedExpandAllMaxYear = None
        self.mCachedOffsets = None


    def duplicate(self, parent=None):
        other = super(VTimezone, self).duplicate(parent=parent)
        other.mID = self.mID
        other.mUTCOffsetSortKey = self.mUTCOffsetSortKey
        return other


    def getType(self):
        return definitions.cICalComponent_VTIMEZONE


    def getMimeComponentName(self):
        # Cannot be sent as a separate MIME object
        return None


    def addComponent(self, comp):
        # We can embed the timezone components only
        if ((comp.getType() == definitions.cICalComponent_STANDARD)
                or (comp.getType() == definitions.cICalComponent_DAYLIGHT)):
            super(VTimezone, self).addComponent(comp)
        else:
            raise ValueError


    def getMapKey(self):
        return self.mID


    def finalise(self):
        # Get TZID
        temp = self.loadValueString(definitions.cICalProperty_TZID)
        if temp is not None:
            self.mID = temp

        # Sort sub-components by DTSTART
        self.mComponents.sort(key=lambda x: x.getStart())

        # Do inherited
        super(VTimezone, self).finalise()


    def validate(self, doFix=False):
        """
        Validate the data in this component and optionally fix any problems, else raise. If
        loggedProblems is not None it must be a C{list} and problem descriptions are appended
        to that.
        """

        fixed, unfixed = super(VTimezone, self).validate(doFix)

        # Must have at least one STANDARD or DAYLIGHT sub-component
        for component in self.mComponents:
            if component.getType() in (definitions.cICalComponent_STANDARD, definitions.cICalComponent_DAYLIGHT):
                break
        else:
            # Cannot fix a missing required component
            logProblem = "[%s] At least one component must be present: %s or %s" % (
                self.getType(),
                definitions.cICalComponent_STANDARD,
                definitions.cICalComponent_DAYLIGHT,
            )
            unfixed.append(logProblem)

        return fixed, unfixed


    def getID(self):
        return self.mID


    def getUTCOffsetSortKey(self):
        if self.mUTCOffsetSortKey is None:
            # Take time from first element
            if len(self.mComponents) > 0:
                # Initial offset provides the primary key
                utc_offset1 = self.mComponents[0].getUTCOffset()

                # Presence of secondary is the next key
                utc_offset2 = utc_offset1
                if len(self.mComponents) > 1:
                    utc_offset2 = self.mComponents[1].getUTCOffset()

                # Create key
                self.mUTCOffsetSortKey = (utc_offset1 + utc_offset2) / 2
            else:
                self.mUTCOffsetSortKey = 0

        return self.mUTCOffsetSortKey


    def getTimezoneOffsetSeconds(self, dt, relative_to_utc=False):
        """
        Caching implementation of expansion. We cache the entire set of transitions up to one year ahead
        of the requested time.

        We need to handle calculating the offset based on both a local time and a UTC time. The later
        is needed when converting from one timezone offset to another which is best done by determining
        the UTC time as an intermediate value.

        @param dt: a date-time to determine the offset for
        @type dt: L{DateTime}
        @param relative_to_utc: if L{False}, then the L{dt} value is the local time for which an
            offset is desired, if L{True}, then the L{dt} value is a UTC time for which an
            offset is desired.
        @type relative_to_utc: L{bool}
        """

        # Need to make the incoming date-time relative to the DTSTART in the
        # timezone component for proper comparison.
        # This means making the incoming date-time a floating (no timezone)
        # item
        temp = dt.duplicate()
        temp.setTimezoneID(None)

        # Check whether we need to recache
        if self.mCachedExpandAllMaxYear is None or temp.mYear >= self.mCachedExpandAllMaxYear:
            cacheMax = temp.duplicate()
            cacheMax.setHHMMSS(0, 0, 0)
            cacheMax.offsetYear(2)
            cacheMax.setMonth(1)
            cacheMax.setDay(1)
            self.mCachedExpandAll = self.expandAll(None, cacheMax)
            self.mCachedExpandAllMaxYear = cacheMax.mYear
            self.mCachedOffsets = {}

        # Now search for the transition just below the time we want
        if len(self.mCachedExpandAll):
            cacheKey = (temp.mYear, temp.mMonth, temp.mDay, temp.mHours, temp.mMinutes, relative_to_utc)
            i = self.mCachedOffsets.get(cacheKey)
            if i is None:
                i = VTimezone.tuple_bisect_right(self.mCachedExpandAll, temp, relative_to_utc)
                if len(self.mCachedOffsets) >= self.UTCOFFSET_CACHE_MAX_ENTRIES:
                    self.mCachedOffsets = {}
                self.mCachedOffsets[cacheKey] = i
            if i != 0:
                return self.mCachedExpandAll[i - 1][3]

        return 0


    def getTimezoneDescriptor(self, dt):
        result = ""

        # Get the closet matching element to the time
        found = self.findTimezoneElement(dt)

        # Get it
        if found is not None:
            if len(found.getTZName()) == 0:
                tzoffset = found.getUTCOffset()
                negative = False
                if tzoffset < 0:
                    tzoffset = -tzoffset
                    negative = True
                result = ("+", "-")[negative]
                hours_offset = tzoffset / (60 * 60)
                if hours_offset < 10:
                    result += "0"
                result += str(hours_offset)
                mins_offset = (tzoffset / 60) % 60
                if mins_offset < 10:
                    result += "0"
                result += str(mins_offset)
            else:
                result = "("
                result += found.getTZName()
                result += ")"

        return result


    def mergeTimezone(self, tz):
        pass


    @staticmethod
    def tuple_bisect_right(a, x, relative_to_utc=False):
        """
        Same as bisect_right except that the values being compared are the first elements
        of a tuple.
        """

        lo = 0
        hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if x < a[mid][1 if relative_to_utc else 0]:
                hi = mid
            else:
                lo = mid + 1
        return lo


    def findTimezoneElement(self, dt):
        # Need to make the incoming date-time relative to the DTSTART in the
        # timezone component for proper comparison.
        # This means making the incoming date-time a floating (no timezone)
        # item
        temp = dt.duplicate()
        temp.setTimezoneID(None)

        # Had to rework this because some VTIMEZONEs have sub-components where the DST instances are interleaved. That
        # means we have to evaluate each and every sub-component to find the instance immediately less than the time we are checking.

        # Now do the expansion for each one found and pick the lowest
        found = None
        dt_found = DateTime()

        for item in self.mComponents:
            dt_item = item.expandBelow(temp)
            if temp >= dt_item:
                if found is not None:
                    # Compare with the one previously cached and switch to this
                    # one if newer
                    if dt_item > dt_found:
                        found = item
                        dt_found = dt_item
                else:
                    found = item
                    dt_found = dt_item

        return found


    def expandAll(self, start, end, with_name=False):
        results = []
        for item in self.mComponents:
            results.extend(item.expandAll(start, end, with_name))

        utc_results = []
        for items in set(results):
            items = list(items)
            utcdt = items[0].duplicate()
            utcdt.offsetSeconds(-items[1])
            utcdt.setTimezoneUTC(True)
            items.insert(1, utcdt)
            utc_results.append(tuple(items))
        utc_results.sort(key=lambda x: x[0].getPosixTime())
        return utc_results


    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_TZID,
            definitions.cICalProperty_LAST_MODIFIED,
            definitions.cICalProperty_TZURL,
        )


    @staticmethod
    def sortByUTCOffsetComparator(tz1, tz2):
        sort1 = tz1.getUTCOffsetSortKey()
        sort2 = tz2.getUTCOffsetSortKey()
        if sort1 == sort2:
            return tz1.getID().compareToIgnoreCase(tz2.getID())
        else:
            return (1, -1)[sort1 < sort2]

Component.registerComponent(definitions.cICalComponent_VTIMEZONE, VTimezone)
