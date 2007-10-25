##
#    Copyright (c) 2007 Cyrus Daboo. All rights reserved.
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

from component import PyCalendarComponent
from datetime import PyCalendarDateTime
import definitions

class PyCalendarVTimezone(PyCalendarComponent):

    sBeginDelimiter = definitions.cICalComponent_BEGINVTIMEZONE

    sEndDelimiter = definitions.cICalComponent_ENDVTIMEZONE

    @staticmethod
    def getVBegin():
        return PyCalendarVTimezone.sBeginDelimiter

    @staticmethod
    def getVEnd():
        return PyCalendarVTimezone.sEndDelimiter

    def __init__(self, calendar=None, copyit=None):
        if calendar is not None:
            super(PyCalendarVTimezone, self).__init__(calendar=calendar)
            self.mID = ""
            self.mSortKey = 1
        elif copyit is not None:
            super(PyCalendarVTimezone, self).__init__(copyit=copyit)
            self.mID = copyit.mID
            self.mSortKey = copyit.mSortKey

    def clone_it(self):
        return PyCalendarVTimezone(copyit=self)

    def getType(self):
        return PyCalendarComponent.eVTIMEZONE

    def getBeginDelimiter(self):
        return PyCalendarVTimezone.sBeginDelimiter

    def getEndDelimiter(self):
        return PyCalendarVTimezone.sEndDelimiter

    def getMimeComponentName(self):
        # Cannot be sent as a separate MIME object
        return None

    def addComponent(self, comp):
        # We can embed the timezone components only
        if ((comp.getType() == PyCalendarComponent.eVTIMEZONESTANDARD)
                or (comp.getType() == PyCalendarComponent.eVTIMEZONEDAYLIGHT)):
            if self.mEmbedded is None:
                self.mEmbedded = []
            self.mEmbedded.append(comp)
            comp.setEmbedder(self)
            return True
        else:
            return False

    def getMapKey(self):
        return self.mID

    def finalise(self):
        # Get TZID
        temp = self.loadValueString(definitions.cICalProperty_TZID)
        if temp is not None:
            self.mID = temp

        # Sort sub-components by DTSTART
        if self.mEmbedded is not None:
            from pycalendar.vtimezoneelement import PyCalendarVTimezoneElement
            self.mEmbedded.sort(PyCalendarVTimezoneElement.sort_dtstart)

        # Do inherited
        super(PyCalendarVTimezone, self).finalise()

    def getID(self):
        return self.mID

    def getSortKey(self):
        if self.mSortKey == 1:
            # Take time from first element
            if (self.mEmbedded is not None) and (len(self.mEmbedded) > 0):
                # Initial offset provides the primary key
                utc_offset1 = self.mEmbedded[0].getUTCOffset()

                # Presence of secondary is the next key
                utc_offset2 = utc_offset1
                if len(self.mEmbedded) > 1:
                    utc_offset2 = self.mEmbedded[1].getUTCOffset()

                # Create key
                self.mSortKey = (utc_offset1 + utc_offset2) / 2
            else:
                self.mSortKey = 0

        return self.mSortKey

    def getTimezoneOffsetSeconds(self, dt):
        # Get the closet matching element to the time
        found = self.findTimezoneElement(dt)

        # Return it
        if found is None:
            return 0
        else:
            # Get its offset
            return found.getUTCOffset()

    def getTimezoneDescriptor(self, dt):
        result = ""

        # Get the closet matching element to the time
        found = self.findTimezoneElement(dt)

        # Get it
        if found is not None:
            if found.getTZName().length() == 0:
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

    def findTimezoneElement(self, dt):
        # Need to make the incoming date-time relative to the DTSTART in the
        # timezone component for proper comparison.
        # This means making the incoming date-time a floating (no timezone)
        # item
        temp = PyCalendarDateTime(copyit=dt)
        temp.setTimezoneID(None)

        # New scheme to avoid unneccessary timezone recurrence expansion:

        # Look for the standard and daylight components with a start time just
        # below the requested date-time
        found_std = None
        found_day = None

        if self.mEmbedded is not None:
            for item in self.mEmbedded:
                if item.getStart() < temp:
                    if item.getType() == PyCalendarComponent.eVTIMEZONESTANDARD:
                        found_std = item
                    else:
                        found_day = item

        # Now do the expansion for each one found and pick the lowest
        found = None
        dt_found = PyCalendarDateTime()

        if found_std is not None:
            dt_item = found_std.expandBelow(temp)
            if temp >= dt_item:
                found = found_std
                dt_found = dt_item

        if found_day is not None:
            dt_item = found_day.expandBelow(temp)
            if temp >= dt_item:
                if found is not None:
                    # Compare with the one previously cached and switch to this
                    # one if newer
                    if dt_item > dt_found:
                        found = found_day
                        dt_found = dt_item
                else:
                    found = found_day
                    dt_found = dt_item

        return found

    def expandAll(self, start, end):
        results = []
        if self.mEmbedded is not None:
            for item in self.mEmbedded:
                results.extend(item.expandAll(start, end))
        results = [x for x in set(results)]
        def sortit(e1, e2):
            return PyCalendarDateTime.sort(e1[0], e2[0])
        results.sort(cmp=sortit)
        return results

    @staticmethod
    def sortComparator(tz1, tz2):
            sort1 = tz1.getSortKey()
            sort2 = tz2.getSortKey()
            if sort1 == sort2:
                return tz1.getID().compareToIgnoreCase(tz2.getID())
            else:
                return (1, -1)[sort1 < sort2]
