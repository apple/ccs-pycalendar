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

from pycalendar import definitions
from pycalendar import itipdefinitions
from pycalendar.component import PyCalendarComponent
from pycalendar.datetime import PyCalendarDateTime
from pycalendar.freebusy import PyCalendarFreeBusy
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS
from pycalendar.period import PyCalendarPeriod
from pycalendar.periodvalue import PyCalendarPeriodValue
from pycalendar.property import PyCalendarProperty
from pycalendar.value import PyCalendarValue

class PyCalendarVFreeBusy(PyCalendarComponent):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTAMP,
        definitions.cICalProperty_UID,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_CONTACT,
        definitions.cICalProperty_DTSTART,
        definitions.cICalProperty_DTEND,
        definitions.cICalProperty_ORGANIZER,
        definitions.cICalProperty_URL,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):
        super(PyCalendarVFreeBusy, self).__init__(parent=parent)
        self.mStart = PyCalendarDateTime()
        self.mHasStart = False
        self.mEnd = PyCalendarDateTime()
        self.mHasEnd = False
        self.mDuration = False
        self.mCachedBusyTime = False
        self.mSpanPeriod = None
        self.mBusyTime = None

    def duplicate(self, parent=None):
        other = super(PyCalendarVFreeBusy, self).duplicate(parent=parent)
        other.mStart = self.mStart.duplicate()
        other.mHasStart = self.mHasStart
        other.mEnd = self.mEnd.duplicate()
        other.mHasEnd = self.mHasEnd
        other.mDuration = self.mDuration
        other.mCachedBusyTime = False
        other.mBusyTime = None
        return other

    def getType(self):
        return definitions.cICalComponent_VFREEBUSY

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VFREEBUSY

    def finalise(self):
        # Do inherited
        super(PyCalendarVFreeBusy, self).finalise()

        # Get DTSTART
        temp = self.loadValueDateTime(definitions.cICalProperty_DTSTART)
        self.mHasStart = temp is not None
        if self.mHasStart:
            self.mStart = temp

        # Get DTEND
        temp = self.loadValueDateTime(definitions.cICalProperty_DTEND)
        if temp is None:
            # Try DURATION instead
            temp = self.loadValueDuration(definitions.cICalProperty_DURATION)
            if temp is not None:
                self.mEnd = self.mStart + temp
                self.mDuration = True
            else:
                # Force end to start, which will then be fixed to sensible
                # value later
                self.mEnd = self.mStart
        else:
            self.mHasEnd = True
            self.mDuration = False
            self.mEnd = temp

    def fixStartEnd(self):
        # End is always greater than start if start exists
        if self.mHasStart and self.mEnd <= self.mStart:
            # Use the start
            self.mEnd = self.mStart.duplicate()
            self.mDuration = False

            # Adjust to appropiate non-inclusive end point
            if self.mStart.isDateOnly():
                self.mEnd.offsetDay(1)

                # For all day events it makes sense to use duration
                self.mDuration = True
            else:
                # Use end of current day
                self.mEnd.offsetDay(1)
                self.mEnd.setHHMMSS(0, 0, 0)

    def getStart(self):
        return self.mStart

    def hasStart(self):
        return self.mHasStart

    def getEnd(self):
        return self.mEnd

    def hasEnd(self):
        return self.mHasEnd

    def useDuration(self):
        return self.mDuration

    def getSpanPeriod(self):
        return self.mSpanPeriod

    def getBusyTime(self):
        return self.mBusyTime

    def editTiming(self):
        # Updated cached values
        self.mHasStart = False
        self.mHasEnd = False
        self.mDuration = False
        self.mStart.setToday()
        self.mEnd.setToday()

        # Remove existing DTSTART & DTEND & DURATION & DUE items
        self.removeProperties(definitions.cICalProperty_DTSTART)
        self.removeProperties(definitions.cICalProperty_DTEND)
        self.removeProperties(definitions.cICalProperty_DURATION)

    def editTimingStartEnd(self, start, end):
        # Updated cached values
        self.mHasStart = self.mHasEnd = True
        self.mStart = start
        self.mEnd = end
        self.mDuration = False
        self.fixStartEnd()

        # Remove existing DTSTART & DTEND & DURATION & DUE items
        self.removeProperties(definitions.cICalProperty_DTSTART)
        self.removeProperties(definitions.cICalProperty_DTEND)
        self.removeProperties(definitions.cICalProperty_DURATION)

        # Now create properties
        prop = PyCalendarProperty(definitions.cICalProperty_DTSTART, start)
        self.addProperty(prop)

        # If its an all day event and the end one day after the start, ignore it
        temp = start.duplicate()
        temp.offsetDay(1)
        if not start.isDateOnly() or end != temp:
            prop = PyCalendarProperty(definitions.cICalProperty_DTEND, end)
            self.addProperty(prop)

    def editTimingStartDuration(self, start, duration):
        # Updated cached values
        self.mHasStart = True
        self.mHasEnd = False
        self.mStart = start
        self.mEnd = start + duration
        self.mDuration = True

        # Remove existing DTSTART & DTEND & DURATION & DUE items
        self.removeProperties(definitions.cICalProperty_DTSTART)
        self.removeProperties(definitions.cICalProperty_DTEND)
        self.removeProperties(definitions.cICalProperty_DURATION)
        self.removeProperties(definitions.cICalProperty_DUE)

        # Now create properties
        prop = PyCalendarProperty(definitions.cICalProperty_DTSTART, start)
        self.addProperty(prop)

        # If its an all day event and the duration is one day, ignore it
        if (not start.isDateOnly() or (duration.getWeeks() != 0)
                or (duration.getDays() > 1)):
            prop = PyCalendarProperty(definitions.cICalProperty_DURATION, duration)
            self.addProperty(prop)

    # Generating info
    def expandPeriodComp(self, period, list):
        # Cache the busy-time details if not done already
        if not self.mCachedBusyTime:
            self.cacheBusyTime()

        # See if period intersects the busy time span range
        if (self.mBusyTime is not None) and period.isPeriodOverlap(self.mSpanPeriod):
            list.append(self)

    def expandPeriodFB(self, period, list):
        # Cache the busy-time details if not done already
        if not self.mCachedBusyTime:
            self.cacheBusyTime()

        # See if period intersects the busy time span range
        if (self.mBusyTime is not None) and period.isPeriodOverlap(self.mSpanPeriod):
            for fb in self.mBusyTime:
                list.append(PyCalendarFreeBusy(fb))

    def cacheBusyTime(self):

        # Clear out any existing cache
        self.mBusyTime = []

        # Get all FREEBUSY items and add those that are BUSY
        min_start = PyCalendarDateTime()
        max_end = PyCalendarDateTime()
        props = self.getProperties()
        result = props.get(definitions.cICalProperty_FREEBUSY, ())
        for iter in result:

            # Check the properties FBTYPE attribute
            type = 0
            is_busy = False
            if iter.hasAttribute(definitions.cICalAttribute_FBTYPE):

                fbyype = iter.getAttributeValue(definitions.cICalAttribute_FBTYPE)
                if fbyype.upper() == definitions.cICalAttribute_FBTYPE_BUSY:

                    is_busy = True
                    type = PyCalendarFreeBusy.BUSY

                elif fbyype.upper() == definitions.cICalAttribute_FBTYPE_BUSYUNAVAILABLE:

                    is_busy = True
                    type = PyCalendarFreeBusy.BUSYUNAVAILABLE

                elif fbyype.upper() == definitions.cICalAttribute_FBTYPE_BUSYTENTATIVE:

                    is_busy = True
                    type = PyCalendarFreeBusy.BUSYTENTATIVE

                else:

                    is_busy = False
                    type = PyCalendarFreeBusy.FREE

            else:

                # Default is busy when no attribute
                is_busy = True
                type = PyCalendarFreeBusy.BUSY

            # Add this period
            if is_busy:

                multi = iter.getMultiValue()
                if (multi is not None) and (multi.getType() == PyCalendarValue.VALUETYPE_PERIOD):

                    for o in multi.getValues():

                        # Double-check type
                        period = None
                        if isinstance(o, PyCalendarPeriodValue):
                            period = o
                        
                        # Double-check type
                        if period is not None:

                            self.mBusyTime.append(PyCalendarFreeBusy(type, period.getValue()))
                            
                            if len(self.mBusyTime) == 1:

                                min_start = period.getValue().getStart()
                                max_end = period.getValue().getEnd()

                            else:

                                if min_start > period.getValue().getStart():
                                    min_start = period.getValue().getStart()
                                if max_end < period.getValue().getEnd():
                                    max_end = period.getValue().getEnd()

        # If nothing present, empty the list
        if len(self.mBusyTime) == 0:

            self.mBusyTime = None

        else:

        
            # Sort the list by period
            self.mBusyTime.sort(cmp=lambda x,y: x.getPeriod().getStart().compareDateTime(y.getPeriod().getStart()))

            # Determine range
            start = PyCalendarDateTime()
            end = PyCalendarDateTime()
            if self.mHasStart:
                start = self.mStart
            else:
                start = min_start
            if self.mHasEnd:
                end = self.mEnd
            else:
                end = max_end
            
            self.mSpanPeriod = PyCalendarPeriod(start, end)
        
        self.mCachedBusyTime = True

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_DTSTART,
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_DTEND,
        )
