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
from componentexpanded import PyCalendarComponentExpanded
from datetime import PyCalendarDateTime
from property import PyCalendarProperty
from recurrenceset import PyCalendarRecurrenceSet
from utils import set_difference
import definitions

class PyCalendarComponentRecur(PyCalendarComponent):

    @staticmethod
    def mapKey(uid, rid = None):
        result = "u:" + uid
        if rid is not None:
            result += rid
        return result

    @staticmethod
    def sort_by_dtstart_allday(e1, e2):

        if e1.self.mStart.isDateOnly() and e2.self.mStart.isDateOnly():
            return e1.self.mStart.lt(e2.self.mStart)
        elif e1.self.mStart.isDateOnly():
            return True;
        elif (e2.self.mStart.isDateOnly()):
            return False;
        elif e1.self.mStart.eq(e2.self.mStart):
            if e1.self.mEnd.eq(e2.self.mEnd):
                # Put ones created earlier in earlier columns in day view
                return e1.self.mStamp.lt(e2.self.mStamp)
            else:
                # Put ones that end later in earlier columns in day view
                return e1.self.mEnd.gt(e2.self.mEnd)
        else:
            return e1.self.mStart.lt(e2.self.mStart)

    @staticmethod
    def sort_by_dtstart(e1, e2):
        if e1.self.mStart.eq(e2.self.mStart):
            if (e1.self.mStart.isDateOnly() and e2.self.mStart.isDateOnly() or
                not e1.self.mStart.isDateOnly() and not e2.self.mStart.isDateOnly()):
                return False
            else:
                return e1.self.mStart.isDateOnly()
        else:
            return e1.self.mStart.lt(e2.self.mStart)

    def __init__(self, calendar=None, copyit=None):
        if calendar is not None:
            super(PyCalendarComponentRecur, self).__init__(calendar=calendar)
            self.mMaster = self
            self.mMapKey = None
            self.mSummary = None
            self.mStamp = PyCalendarDateTime()
            self.mHasStamp = False
            self.mStart = PyCalendarDateTime()
            self.mHasStart = False
            self.mEnd = PyCalendarDateTime()
            self.mHasEnd = False
            self.mDuration = False
            self.mHasRecurrenceID = False
            self.mAdjustFuture = False
            self.mAdjustPrior = False
            self.mRecurrenceID = None
            self.mRecurrences = None
        elif copyit is not None:
            super(PyCalendarComponentRecur, self).__init__(copyit)
    
            # Special determination of master
            if copyit.recurring():
                self.mMaster = copyit.mMaster
            else:
                self.mMaster = self
    
            self.mMapKey = copyit.mMapKey
    
            self.mSummary = copyit.mSummary
    
            if (copyit.mStamp != None):
                self.mStamp = PyCalendarDateTime(copyit=copyit.mStamp)
            self.mHasStamp = copyit.mHasStamp
    
            self.mStart = PyCalendarDateTime(copyit=copyit.mStart)
            self.mHasStart = copyit.mHasStart
            self.mEnd = PyCalendarDateTime(copyit=copyit.mEnd)
            self.mHasEnd = copyit.mHasEnd
            self.mDuration = copyit.mDuration
    
            self.mHasRecurrenceID = copyit.mHasRecurrenceID
            self.mAdjustFuture = copyit.mAdjustFuture
            self.mAdjustPrior = copyit.mAdjustPrior
            if copyit.mRecurrenceID != None:
                self.mRecurrenceID = PyCalendarDateTime(copyit.mRecurrenceID)
    
            if copyit.mRecurrences != None:
                self.mRecurrences = PyCalendarRecurrenceSet(copyit.mRecurrences)

    def canGenerateInstance(self):
        return not self.mHasRecurrenceID

    def recurring(self):
        return (self.mMaster != None) and (self.mMaster != self)

    def setMaster(self, master):
        self.mMaster = master
        self.initFromMaster()

    def getMaster(self):
        return self.mMaster

    def getMapKey(self):
        return self.mMapKey

    def getMasterKey(self):
        return PyCalendarComponentRecur.mapKey(self.mUID)

    def initDTSTAMP(self):
        # Save new one
        super(PyCalendarComponentRecur, self).initDTSTAMP()

        # Get the new one
        temp = self.loadValueDateTime(definitions.cICalProperty_DTSTAMP)
        self.mHasStamp = temp is not None
        if self.mHasStamp:
            self.mStamp = temp
    
    def getStamp(self):
        return self.mStamp

    def hasStamp(self):
        return self.mHasStamp

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

    def isRecurrenceInstance(self):
        return self.mHasRecurrenceID

    def isAdjustFuture(self):
        return self.mAdjustFuture

    def isAdjustPrior(self):
        return self.mAdjustPrior

    def getRecurrenceID(self):
        return self.mRecurrenceID

    def isRecurring(self):
        return (self.mRecurrences != None) and self.mRecurrences.hasRecurrence()

    def getRecurrenceSet(self):
        return self.mRecurrences

    def setUID(self, uid):
        super(PyCalendarComponentRecur, self).setUID(uid);

        # Update the map key
        if self.mHasRecurrenceID:
            self.mMapKey = self.mapKey(self.mUID, self.mRecurrenceID.getText())
        else:
            self.mMapKey = self.mapKey(self.mUID)

    def getSummary(self):
        return self.mSummary

    def setSummary(self, summary):
        self.mSummary = summary

    def getDescription(self):
        # Get DESCRIPTION
        txt = self.loadValueString(definitions.cICalProperty_DESCRIPTION)
        if txt is not None:
            return txt
        else:
            return ""

    def getLocation(self):
        # Get LOCATION
        txt = self.loadValueString(definitions.cICalProperty_LOCATION)
        if txt is not None:
            return txt
        else:
            return ""

    def finalise(self):
        super(PyCalendarComponentRecur, self).finalise();

        # Get DTSTAMP
        temp = self.loadValueDateTime(definitions.cICalProperty_DTSTAMP)
        self.mHasStamp = temp is not None
        if self.mHasStamp:
            self.mStamp = temp

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
                self.mHasEnd = False
                self.mEnd = self.mStart.add(temp)
                self.mDuration = True
            else:
                # If no end or duration then use the start
                self.mHasEnd = False
                self.mEnd = PyCalendarDateTime(self.mStart)
                self.mDuration = False
        else:
            self.mHasEnd = True
            self.mEnd = temp
            self.mDuration = False

        # Make sure start/end values are sensible
        self.FixStartEnd();

        # Get SUMMARY
        temp = self.loadValueString(definitions.cICalProperty_SUMMARY)
        if temp is not None:
            self.mSummary = temp

        # Get RECURRENCE-ID
        self.mHasRecurrenceID = (self.countProperty(definitions.cICalProperty_RECURRENCE_ID) != 0)
        if self.mHasRecurrenceID:
            if self.mRecurrenceID is None:
                self.mRecurrenceID = PyCalendarDateTime()
            self.mRecurrenceID = self.loadValueDateTime(definitions.cICalProperty_RECURRENCE_ID)

        # Update the map key
        if self.mHasRecurrenceID:
            self.mMapKey = self.mapKey(self.mUID, self.mRecurrenceID.getText())

            # Also get the RANGE attribute
            attrs = self.findFirstProperty(definitions.cICalProperty_RECURRENCE_ID).getAttributes()
            if attrs.has_key(definitions.cICalAttribute_RANGE):
                self.mAdjustFuture = (attrs[definitions.cICalAttribute_RANGE][0].getFirstValue() == definitions.cICalAttribute_RANGE_THISANDFUTURE)
                self.mAdjustPrior = (attrs[definitions.cICalAttribute_RANGE][0].getFirstValue() == definitions.cICalAttribute_RANGE_THISANDPRIOR)
            else:
                self.mAdjustFuture = False
                self.mAdjustPrior = False
        else:
            self.mMapKey = self.mapKey(self.mUID)

        # May need to create items
        if ((self.countProperty(definitions.cICalProperty_RRULE) != 0)
                or (self.countProperty(definitions.cICalProperty_RDATE) != 0)
                or (self.countProperty(definitions.cICalProperty_EXRULE) != 0)
                or (self.countProperty(definitions.cICalProperty_EXDATE) != 0)):
            if self.mRecurrences is None:
                self.mRecurrences = PyCalendarRecurrenceSet()

            # Get RRULEs
            self.loadValueRRULE(definitions.cICalProperty_RRULE,
                    self.mRecurrences, True);

            # Get RDATEs
            self.loadValueRDATE(definitions.cICalProperty_RDATE,
                    self.mRecurrences, True);

            # Get EXRULEs
            self.loadValueRRULE(definitions.cICalProperty_EXRULE,
                    self.mRecurrences, False);

            # Get EXDATEs
            self.loadValueRDATE(definitions.cICalProperty_EXDATE,
                    self.mRecurrences, False);

    def FixStartEnd(self):
        # End is always greater than start if start exists
        if self.mHasStart and self.mEnd.le(self.mStart):
            # Use the start
            self.mEnd = PyCalendarDateTime(self.mStart)
            self.mDuration = False

            # Adjust to approriate non-inclusive end point
            if self.mStart.isDateOnly():
                self.mEnd.offsetDay(1)

                # For all day events it makes sense to use duration
                self.mDuration = True
            else:
                # Use end of current day
                self.mEnd.offsetDay(1)
                self.mEnd.setHHMMSS(0, 0, 0)

    def expandPeriod(self, period, list):
        # Check for recurrence and True master
        if ((self.mRecurrences is not None) and self.mRecurrences.hasRecurrence()
                and not self.isRecurrenceInstance()):
            # Expand recurrences within the range
            items = []
            self.mRecurrences.expand(self.mStart, period, items);

            # Look for overridden recurrence items
            from pycalendar.calendar import PyCalendar
            cal = PyCalendar.getICalendar(self.getCalendar())
            if cal is not None:
                # Remove recurrence instances from the list of items
                recurs = []
                cal.getRecurrenceInstancesIds(PyCalendarComponent.eVEVENT, self.getUID(), recurs)
                if len(recurs) != 0:
                    temp = []
                    temp = set_difference(items, recurs)
                    items = temp

                    # Now get actual instances
                    instances = []
                    cal.getRecurrenceInstancesItems(PyCalendarComponent.eVEVENT, self.getUID(), instances)

                    # Get list of each ones with RANGE
                    prior = []
                    future = []
                    for iter in instances:
                        if iter.isAdjustPrior():
                            prior.append(iter)
                        if iter.isAdjustFuture():
                            future.append(iter)

                    # Check for special behaviour
                    if prior.isEmpty() and future.isEmpty():
                        # Add each expanded item
                        for iter in items:
                            list.append(self.createExpanded(self, iter))
                    else:
                        # Sort each list first
                        prior.sort(self.sort_by_dtstart)
                        future.sort(self.sort_by_dtstart)

                        # Add each expanded item
                        for iter1 in items:

                            # Now step through each using the slave item
                            # instead of the master as appropriate
                            slave = None

                            # Find most appropriate THISANDPRIOR item
                            for i in range(len(prior) - 1, 0, -1):
                                riter2 = prior[i]
                                if riter2.getStart().gt(iter1):
                                    slave = riter2
                                    break

                            # Find most appropriate THISANDFUTURE item
                            for i in range(len(future) - 1, 0, -1):
                                riter2 = future.elementAt(i)
                                if riter2.getStart().lt(iter1):
                                    slave = riter2
                                    break

                            if slave is None:
                                slave = self
                            list.append(self.createExpanded(slave, iter1))
                else:
                    # Add each expanded item
                    for iter in items:
                        list.append(self.createExpanded(self, iter))

        elif self.withinPeriod(period):
            if self.isRecurrenceInstance():
                rid = self.mRecurrenceID
            else:
                rid = None
            list.append(PyCalendarComponentExpanded(self, rid))

    def withinPeriod(self, period):
        # Check for recurrence
        if ((self.mRecurrences != None) and self.mRecurrences.hasRecurrence()):
            items = []
            self.mRecurrences.expand(self.mStart, period, items)
            return not items.isEmpty()
        else:
            # Does event span the period (assume self.mEnd > self.mStart)
            # Check start (inclusive) and end (exclusive)
            if self.mEnd.le(period.getStart()) or self.mStart.ge(period.getEnd()):
                return False
            else:
                return True

    def changedRecurrence(self):
        # Clear cached values
        if self.mRecurrences is not None:
            self.mRecurrences.changed()

    # Editing
    def editSummary(self, summary):
        # Updated cached value
        self.mSummary = summary

        # Remove existing items
        self.editProperty(definitions.cICalProperty_SUMMARY, summary)

    def editDetails(self, description, location):

        # Edit existing items
        self.editProperty(definitions.cICalProperty_DESCRIPTION, description)
        self.editProperty(definitions.cICalProperty_LOCATION, location)

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
        self.removeProperties(definitions.cICalProperty_DUE)

    def editTimingDue(self, due):
        # Updated cached values
        self.mHasStart = False
        self.mHasEnd = True
        self.mDuration = False
        self.mStart = due
        self.mEnd = due

        # Remove existing DUE & DTSTART & DTEND & DURATION items
        self.removeProperties(definitions.cICalProperty_DUE)
        self.removeProperties(definitions.cICalProperty_DTSTART)
        self.removeProperties(definitions.cICalProperty_DTEND)
        self.removeProperties(definitions.cICalProperty_DURATION)

        # Now create properties
        prop = PyCalendarProperty(definitions.cICalProperty_DUE, due)
        self.addProperty(prop)

    def editTimingStartEnd(self, start, end):
        # Updated cached values
        self.mHasStart = self.mHasEnd = True
        self.mStart = start
        self.mEnd = end
        self.mDuration = False
        self.FixStartEnd()
        # Remove existing DTSTART & DTEND & DURATION & DUE items
        self.removeProperties(definitions.cICalProperty_DTSTART)
        self.removeProperties(definitions.cICalProperty_DTEND)
        self.removeProperties(definitions.cICalProperty_DURATION)
        self.removeProperties(definitions.cICalProperty_DUE)

        # Now create properties
        prop = PyCalendarProperty(definitions.cICalProperty_DTSTART, start)
        self.addProperty(prop)

        # If its an all day event and the end one day after the start, ignore it
        temp = PyCalendarDateTime(start)
        temp.offsetDay(1);
        if not start.isDateOnly() or end.ne(temp):
            prop = PyCalendarProperty(definitions.cICalProperty_DTEND, end)
            self.addProperty(prop)

    def editTimingStartDuration(self, start, duration):
        # Updated cached values
        self.mHasStart = True
        self.mHasEnd = False
        self.mStart = start
        self.mEnd = start.add(duration)
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

    def editRecurrenceSet(self, recurs):
        # Must have items
        if self.mRecurrences is None:
            self.mRecurrences = PyCalendarRecurrenceSet()

        # Updated cached values
        self.mRecurrences = recurs

        # Remove existing RRULE, EXRULE, RDATE & EXDATE
        self.removeProperties(definitions.cICalProperty_RRULE)
        self.removeProperties(definitions.cICalProperty_EXRULE);
        self.removeProperties(definitions.cICalProperty_RDATE);
        self.removeProperties(definitions.cICalProperty_EXDATE);

        # Now create properties
        for iter in self.mRecurrences.getRules():
            prop = PyCalendarProperty(definitions.cICalProperty_RRULE, iter)
            self.addProperty(prop)
        for iter in self.getExrules():
            prop = PyCalendarProperty(definitions.cICalProperty_EXRULE, iter)
            self.addProperty(prop)
        for iter in self.mRecurrences.getDates():
            prop = PyCalendarProperty(definitions.cICalProperty_RDATE, iter)
            self.addProperty(prop)
        for iter in self.mRecurrences.getExdates():
            prop = PyCalendarProperty(definitions.cICalProperty_EXDATE, iter)
            self.addProperty(prop);

    def excludeRecurrence(self, start):
        # Must have items
        if self.mRecurrences is None:
            return

        # Add to recurrence set and clear cache
        self.mRecurrences.subtract(start);

        # Add property
        prop = PyCalendarProperty(definitions.cICalProperty_EXDATE, start);
        self.addProperty(prop)

    def excludeFutureRecurrence(self, start):
        # Must have items
        if self.mRecurrences is None:
            return

        # Adjust RRULES to end before start
        self.mRecurrences.excludeFutureRecurrence(start)

        # Remove existing RRULE & RDATE
        self.removeProperties(definitions.cICalProperty_RRULE)
        self.removeProperties(definitions.cICalProperty_RDATE)

        # Now create properties
        for iter in self.mRecurrences.getRules():
            prop = PyCalendarProperty(definitions.cICalProperty_RRULE, iter)
            self.addProperty(prop)
        for iter in  self.mRecurrences.getDates():
            prop = PyCalendarProperty(definitions.cICalProperty_RDATE, iter)
            self.addProperty(prop)

    # These are overridden to allow missing properties to come from the master
    # component
    def loadValueInteger(self, value_name, type=None):
        # Try to load from this component
        result = super(PyCalendarComponentRecur, self).loadValueInteger(value_name, type)

        # Try to load from master if we didn't get it from this component
        if (result is None) and (self.mMaster is not None) and (self.mMaster != self):
            result = self.mMaster.loadValueInteger(value_name, type)

        return result

    def loadValueString(self, value_name):
        # Try to load from this component
        result = super(PyCalendarComponentRecur, self).loadValueString(value_name)

        # Try to load from master if we didn't get it from this component
        if (result is None) and (self.mMaster is not None) and (self.mMaster != self):
            result = self.mMaster.loadValueString(value_name)

        return result

    def loadValueDateTime(self, value_name):
        # Try to load from this component
        result = super(PyCalendarComponentRecur, self).loadValueDateTime(value_name)

        # Try to load from master if we didn't get it from this component
        if not result and (self.mMaster is not None) and (self.mMaster is not self):
            result = self.mMaster.loadValueDateTime(value_name)

        return result

    def loadValueDuration(self, value_name):
        # Try to load from this component
        result = super(PyCalendarComponentRecur, self).loadValueDuration(value_name)

        # Try to load from master if we didn't get it from this component
        if not result and (self.mMaster is not None) and (self.mMaster is not self):

            result = self.mMaster.loadValueDuration(value_name)
        return result

    def loadValuePeriod(self, value_name):
        # Try to load from this component
        result = super(PyCalendarComponentRecur, self).loadValuePeriod(value_name)

        # Try to load from master if we didn't get it from this component
        if not result and (self.mMaster is not None) and (self.mMaster is not self):
            result = self.mMaster.loadValuePeriod(value_name)

        return result

    def loadValueRRULE(self, value_name, value, add):
        # Try to load from this component
        result = super(PyCalendarComponentRecur, self).loadValueRRULE(value_name, value, add)

        # Try to load from master if we didn't get it from this component
        if not result and (self.mMaster is not None) and (self.mMaster is not self):
            result = self.mMaster.loadValueRRULE(value_name, value, add)

        return result

    def loadValueRDATE(self, value_name, value, add):
        # Try to load from this component
        result = super(PyCalendarComponentRecur, self).loadValueRDATE(value_name, value, add)

        # Try to load from master if we didn't get it from this component
        if not result and (self.mMaster is not None) and (self.mMaster is not self):
            result = self.mMaster.loadValueRDATE(value_name, value, add)

        return result

    def initFromMaster(self):
        # Only if not master
        if self.recurring():
            # Redo this to get cached values from master
            self.finalise()

            # If this component does not have its own start property, use the
            # recurrence id
            # i.e. the start time of this instance has not changed - something
            # else has
            if not self.hasProperty(definitions.cICalProperty_DTSTART):
                self.mStart = self.mRecurrenceID

            # If this component does not have its own end/duration property,
            # the determine
            # the end from the master duration
            if (not self.hasProperty(definitions.cICalProperty_DTEND) and
                not self.hasProperty(definitions.cICalProperty_DURATION)):
                # End is based on original events settings
                self.mEnd = self.mStart.add(self.mMaster.getEnd().subtract(self.mMaster.getStart()))

            # If this instance has a duration, but no start of its own, then we
            # need to readjust the end
            # to account for the start being changed to the recurrence id
            elif (self.hasProperty(definitions.cICalProperty_DURATION) and
                  not self.hasProperty(definitions.cICalProperty_DTSTART)):
                temp = self.loadValueDuration(definitions.cICalProperty_DURATION)
                self.mEnd = self.mStart.add(temp)

    def createExpanded(self, master, recurid):
        return PyCalendarComponentExpanded(master, recurid)
