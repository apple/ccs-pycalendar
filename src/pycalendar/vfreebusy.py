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
from freebusy import PyCalendarFreeBusy
from period import PyCalendarPeriod
from periodvalue import PyCalendarPeriodValue
from value import PyCalendarValue
import definitions
import itipdefinitions

class PyCalendarVFreeBusy(PyCalendarComponent):

    sBeginDelimiter = definitions.cICalComponent_BEGINVFREEBUSY

    sEndDelimiter = definitions.cICalComponent_ENDVFREEBUSY

    @staticmethod
    def getVBegin():
        return PyCalendarVFreeBusy.sBeginDelimiter

    @staticmethod
    def gGetVEnd():
        return PyCalendarVFreeBusy.sEndDelimiter

    def __init__(self, calendar=None, copyit=None):
        if calendar is not None:
            super(PyCalendarVFreeBusy, self).__init__(calendar=calendar)
            self.mStart = PyCalendarDateTime()
            self.mHasStart = False
            self.mEnd = PyCalendarDateTime()
            self.mHasEnd = False
            self.mDuration = False
            self.mCachedBusyTime = False
            self.mSpanPeriod = None
            self.mBusyTime = None
        elif copyit is not None:
            super(PyCalendarVFreeBusy, self).__init__(copyit=copyit)
            self.mStart = PyCalendarDateTime(copyit.mStart)
            self.mHasStart = copyit.mHasStart
            self.mEnd = PyCalendarDateTime(copyit.mEnd)
            self.mHasEnd = copyit.mHasEnd
            self.mDuration = copyit.mDuration
            self.mCachedBusyTime = False
            self.mBusyTime = None

    def clone_it(self):
        return PyCalendarVFreeBusy(self)

    def getType(self):
        return PyCalendarComponent.eVFREEBUSY

    def getBeginDelimiter(self):
        return PyCalendarVFreeBusy.sBeginDelimiter

    def getEndDelimiter(self):
        return PyCalendarVFreeBusy.sEndDelimiter

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
                self.mEnd = self.mStart.add(temp)
                self.mDuration = True
            else:
                # Force end to start, which will then be fixed to sensible
                # value later
                self.mEnd = self.mStart
        else:
            self.mHasEnd = True
            self.mDuration = False
            self.mEnd = temp

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
        result = props.find(definitions.cICalProperty_FREEBUSY)
        for iter in result:

            # Check the properties FBTYPE attribute
            type = 0
            is_busy = False
            if iter.hasAttribute(definitions.cICalAttribute_FBTYPE):

                fbyype = iter.getAttributeValue(definitions.cICalAttribute_FBTYPE)
                if fbyype.toupper() == definitions.cICalAttribute_FBTYPE_BUSY:

                    is_busy = True
                    type = PyCalendarFreeBusy.BUSY

                elif fbyype.toupper() == definitions.cICalAttribute_FBTYPE_BUSYUNAVAILABLE:

                    is_busy = True
                    type = PyCalendarFreeBusy.BUSYUNAVAILABLE

                elif fbyype.toupper() == definitions.cICalAttribute_FBTYPE_BUSYTENTATIVE:

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

                                if min_start.gt(period.getValue().getStart()):
                                    min_start = period.getValue().getStart()
                                if max_end.lt(period.getValue().getEnd()):
                                    max_end = period.getValue().getEnd()

        # If nothing present, empty the list
        if len(self.mBusyTime) == 0:

            self.mBusyTime = None

        else:

        
            # Sort the list by period
            self.mBusyTime.sort()

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
