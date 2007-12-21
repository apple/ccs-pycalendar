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
from componentbase import PyCalendarComponentBase
from componentdb import PyCalendarComponentDB
from componentexpanded import PyCalendarComponentExpanded
from componentrecur import PyCalendarComponentRecur
from datetime import PyCalendarDateTime
from freebusy import PyCalendarFreeBusy
from period import PyCalendarPeriod
from property import PyCalendarProperty
from utils import readFoldedLine
from valarm import PyCalendarVAlarm
from vevent import PyCalendarVEvent
from vfreebusy import PyCalendarVFreeBusy
from vjournal import PyCalendarVJournal
from vtimezone import PyCalendarVTimezone
from vtimezonedaylight import PyCalendarVTimezoneDaylight
from vtimezonestandard import PyCalendarVTimezoneStandard
from vtodo import PyCalendarVToDo
import definitions

class PyCalendar(PyCalendarComponentBase):

    REMOVE_ALL = 0
    REMOVE_ONLY_THIS = 1
    REMOVE_THIS_AND_FUTURE = 2

    FIND_EXACT = 0
    FIND_MASTER = 1

    VEVENT = 0
    VTODO = 1
    VJOURNAL = 2
    VFREEBUSY = 3
    VTIMEZONE = 4
    MAXV = 5

    # static attributes
    sICalendars = {}
    sICalendarRefCtr = 1
    sICalendar = None

    sProdID = "-//mulberrymail.com//Mulberry v4.0//EN"
    sDomain = "mulberrymail.com"

    @staticmethod
    def getICalendar(ref):
        if PyCalendar.sICalendars.has_key(ref):
            return PyCalendar.sICalendars[ref]
        else:
            return None

    @staticmethod
    def loadStatics():
        PyCalendar.initComponents()

    @staticmethod
    def setPRODID(prodid):
        PyCalendar.sProdID = prodid

    @staticmethod
    def setDomain(domain):
        PyCalendar.sDomain = domain

    def __init__(self):
        super(PyCalendar, self).__init__()

        self.mICalendarRef = ++PyCalendar.sICalendarRefCtr
        PyCalendar.sICalendars[self.mICalendarRef] = self
    
        self.mReadOnly = False
        self.mDirty = False
        self.mTotalReplace = False

        self.mName = ""
        self.mDescription = ""
    
        self.addDefaultProperties()
    
        # Special init for static item
        if self is PyCalendar.sICalendar:
            self.initDefaultTimezones()

        self.mV = []
        for i in range(PyCalendar.MAXV):
            self.mV.append(PyCalendarComponentDB())

        # Special init for static item
        if self is PyCalendar.sICalendar:
            self.initDefaultTimezones()
    
    def close(self):
        # Clean up the map items
        for v in self.mV:
            v.close()

    def getRef(self):
        return self.mICalendarRef

    def remove(self):
        # Broadcast closing before removing components
        # Broadcast_Message(eBroadcast_Closed, this)
    
        # Clean up the map items
        for v in self.mV:
            v.removeAllComponents()
    
        del PyCalendar.sICalendars[self.mICalendarRef]

    def getName(self):
        return self.mName
    
    def setName(self, name):
        self.mName = name

    def editName(self, name):
        if self.mName != name:
            # Updated cached value
            self.mName = name
    
            # Remove existing items
            self.removeProperties(definitions.cICalProperty_XWRCALNAME)
            
            # Now create properties
            if name.length():
                self.ddProperty(PyCalendarProperty(definitions.cICalProperty_XWRCALNAME, name))
            
            # Mark as dirty
            self.setDirty()
            
            # Broadcast change
            #Broadcast_Message(eBroadcast_Edit, this)

    def getDescription(self):
        return self.mDescription
    
    def setDescription(self, description):
        self.mDescription = description

    def editDescription(self, description):
        if self.mDescription != description:
            # Updated cached value
            self.mDescription = description
    
            # Remove existing items
            self.removeProperties(definitions.cICalProperty_XWRCALDESC)
            
            # Now create properties
            if description.length():
                self.addProperty(PyCalendarProperty(definitions.cICalProperty_XWRCALDESC, description))
            
            # Mark as dirty
            self.setDirty()
            
            # Broadcast change
            #Broadcast_Message(eBroadcast_Edit, this)

    def getMethod(self):
        result = ""
        if self.hasProperty(definitions.cICalProperty_METHOD):
            result = self.loadValueString(definitions.cICalProperty_METHOD)
        return result


    def finalise(self):
        # Get calendar name if present
    
        # Get X-WR-CALNAME
        temps = self.loadValueString(definitions.cICalProperty_XWRCALNAME)
        if temps is not None:
            self.mName = temps
    
        # Get X-WR-CALDESC
        temps = self.loadValueString(definitions.cICalProperty_XWRCALDESC)
        if temps is not None:
            self.mDescription = temps

    def parse(self, ins):
        # Always init rhe component maps
        self.initComponents()
    
        result = False
    
        LOOK_FOR_VCALENDAR = 0
        GET_PROPERTY_OR_COMPONENT = 1
        GET_COMPONENT_PROPERTY = 2
        GET_SUB_COMPONENT_PROPERTY = 3
    
        state = LOOK_FOR_VCALENDAR
    
        # Get lines looking for start of calendar
        lines = ["", ""]
        comp = None
        prevcomp = None
        compmap = None
    
        while readFoldedLine(ins, lines):
            if state == LOOK_FOR_VCALENDAR:

                # Look for start
                if lines[0] == definitions.cICalComponent_BEGINVCALENDAR:
                    # Next state
                    state = GET_PROPERTY_OR_COMPONENT
    
                    # Indicate success at this point
                    result = True

            elif state == GET_PROPERTY_OR_COMPONENT:

                # Parse property or look for start of component
                if PyCalendar.sComponents.has_key(lines[0]):

                    # Start a new component
                    comp = PyCalendar.makeComponent(PyCalendar.sComponents[lines[0]].mID, self.getRef())
    
                    # Set the marker for the end of this component and the map to store it in
                    compmap = self.getComponents(PyCalendar.sComponents[lines[0]].mType)
    
                    # Change state
                    state = GET_COMPONENT_PROPERTY

                elif lines[0] == definitions.cICalComponent_ENDVCALENDAR:

                    # Finalise the current calendar
                    self.finalise()
    
                    # Change state
                    state = LOOK_FOR_VCALENDAR

                else:

                    # Parse attribute/value for top-level calendar item
                    prop = PyCalendarProperty()
                    if prop.parse(lines[0]):

                        # Check for valid property
                        if not self.validProperty(prop):
                            return False
                        elif not self.ignoreProperty(prop):
                            self.addProperty(prop)

            elif state in (GET_COMPONENT_PROPERTY, GET_SUB_COMPONENT_PROPERTY):

                # Look for end of current component
                if lines[0] == comp.getEndDelimiter():

                    # Finalise the component (this caches data from the properties)
                    comp.finalise()
    
                    # Check whether this is embedded
                    if prevcomp != None:

                        # Embed component in parent and reset to use parent
                        if not prevcomp.addComponent(comp):
                            comp = None
                        comp = prevcomp
                        prevcomp = None
    
                        # Reset state
                        state = GET_COMPONENT_PROPERTY

                    else:

                        # Check for valid component
                        if not compmap.addComponent(comp):
                            comp = None
                        comp = None
                        compmap = None
    
                        # Reset state
                        state = GET_PROPERTY_OR_COMPONENT

                else:

                    # Look for start of embedded component (can only do once)
                    if (state != GET_SUB_COMPONENT_PROPERTY) and PyCalendar.sEmbeddedComponents.has_key(lines[0]):

                        # Start a new component (saving off the current one)
                        prevcomp = comp
                        comp = PyCalendar.makeComponent(PyCalendar.sEmbeddedComponents[lines[0]].mID, self.getRef())
    
                        # Reset state
                        state = GET_SUB_COMPONENT_PROPERTY

                    else:

                        # Parse attribute/value and store in component
                        prop = PyCalendarProperty()
                        if prop.parse(lines[0]):
                            comp.addProperty(prop)
    
        # We need to store all timezones in the static object so they can be accessed by any date object
        if self is PyCalendar.sICalendar:
            PyCalendar.sICalendar.mergeTimezones(self)
    
        return result
    
    def parseComponent(self, ins, rurl, etag):
        
        # Always init rhe component maps
        self.initComponents()
    
        result = None
    
        LOOK_FOR_VCALENDAR = 0
        GET_PROPERTY_OR_COMPONENT = 1
        GET_COMPONENT_PROPERTY = 2
        GET_SUB_COMPONENT_PROPERTY = 3
        GOT_VCALENDAR = 4
    
        state = LOOK_FOR_VCALENDAR
    
        # Get lines looking for start of calendar
        lines = ["", ""]
        comp = None
        prevcomp = None
        compmap = None
        got_timezone = False
    
        while readFoldedLine(ins, lines):

            if state == LOOK_FOR_VCALENDAR:

                # Look for start
                if lines[0] == definitions.cICalComponent_BEGINVCALENDAR:
                    # Next state
                    state = GET_PROPERTY_OR_COMPONENT

            elif state == GET_PROPERTY_OR_COMPONENT:

                # Parse property or look for start of component
                if PyCalendar.sComponents.has_key(lines[0]):

                    # Start a new component
                    comp = PyCalendar.makeComponent(PyCalendar.sComponents[lines[0]].mID, self.getRef())
                    
                    # Cache as result - but only the first one, we ignore the rest
                    if result is None:
                        result = comp
    
                    # Set the marker for the end of this component and the map to store it in
                    compmap = self.getComponents(PyCalendar.sComponents[lines[0]].mType)
    
                    # Look for timezone component to trigger timezone merge only if one is present
                    if PyCalendar.sComponents[lines[0]].mType == PyCalendarComponent.eVTIMEZONE:
                        got_timezone = True
    
                    # Change state
                    state = GET_COMPONENT_PROPERTY

                elif lines[0] == definitions.cICalComponent_ENDVCALENDAR:

                    # Change state
                    state = GOT_VCALENDAR

                else:

                    # Ignore top-level items
                    pass

            elif state in (GET_COMPONENT_PROPERTY, GET_SUB_COMPONENT_PROPERTY):
                # Look for end of current component
                if lines[0] == comp.getEndDelimiter():

                    # Finalise the component (this caches data from the properties)
                    comp.finalise()
                    comp.setRURL(rurl)
                    comp.setETag(etag)
    
                    # Check whether this is embedded
                    if prevcomp is not None:

                        # Embed component in parent and reset to use parent
                        if not prevcomp.addComponent(comp):
                            comp = None
                        comp = prevcomp
                        prevcomp = None
    
                        # Reset state
                        state = GET_COMPONENT_PROPERTY

                    else:

                        # Check for valid component
                        if not compmap.addComponent(comp):

                            if result == comp:
                                result = None
                            comp = None

                        comp = None
                        compmap = None
    
                        # Reset state
                        state = GET_PROPERTY_OR_COMPONENT

                else:

                    # Look for start of embedded component (can only do once)
                    if (state != GET_SUB_COMPONENT_PROPERTY) and PyCalendar.sEmbeddedComponents.has_key(lines[0]):

                        # Start a new component (saving off the current one)
                        prevcomp = comp
                        comp = PyCalendar.makeComponent(PyCalendar.sEmbeddedComponents[lines[0]].mID, self.getRef())
    
                        # Reset state
                        state = GET_SUB_COMPONENT_PROPERTY

                    else:

                        # Parse attribute/value and store in component
                        prop = PyCalendarProperty
                        if prop.parse(lines[0]):
                            comp.addProperty(prop)
            
            # Exit if we have one - ignore all the rest
            if state == GOT_VCALENDAR:
                break
    
        # We need to store all timezones in the static object so they can be accessed by any date object
        # Only do this if we read in a timezone
        if got_timezone and (self is not PyCalendar.sICalendar):
            PyCalendar.sICalendar.mergeTimezones(self)
    
        return result
        
    def generate(self, os, for_cache = False):
        # Make sure all required timezones are in this object
        self.includeTimezones()
        
        # Write header
        os.write(definitions.cICalComponent_BEGINVCALENDAR)
        os.write("\n")
        
        # Write properties (we always handle PRODID & VERSION)
        self.writeProperties(os)
        
        # Write out each type of component (not VALARMS which are embedded in others)
        # Do VTIMEZONES at the start
        self.generateDB(os, self.mV[PyCalendar.VTIMEZONE], for_cache)
        self.generateDB(os, self.mV[PyCalendar.VEVENT], for_cache)
        self.generateDB(os, self.mV[PyCalendar.VTODO], for_cache)
        self.generateDB(os, self.mV[PyCalendar.VJOURNAL], for_cache)
        self.generateDB(os, self.mV[PyCalendar.VFREEBUSY], for_cache)
        
        # Write trailer
        os.write(definitions.cICalComponent_ENDVCALENDAR)
        os.write("\n")
        
    def generateOne(self, os, comp):
        # Write header
        os.write(definitions.cICalComponent_BEGINVCALENDAR)
        os.write("\n")
   
        # Write properties (we always handle PRODID & VERSION)
        self.writeProperties(os)
    
        # Make sure each timezone is written out
        tzids = set()
        comp.getTimezones(tzids)
        for tzid in tzids:

            tz = self.getTimezone(tzid)
            if tz == None:

                # Find it in the static object
                tz = PyCalendar.sICalendar.getTimezone(tzid)
            
            if tz is not None:
                tz.generate(os, False)
    
        # Check for recurring component and potentially write out all instances
        if isinstance(comp, PyCalendarComponentRecur):

            # Write this one out first
            comp.generate(os, False)
            
            # Get list of all instances
            instances = self.getRecurrenceInstances(comp.getType(), comp.getUID())
    
            # Write each instance out
            for r in instances:
                # Write the component
                r.generate(os. False)

        else:
            # Write the component
            comp.generate(os, False)
    
        # Write trailer
        os.write(definitions.cICalComponent_ENDVCALENDAR)
        os.write("\n")

    # Get components
    def getVEventsDB(self):
        return self.mV[PyCalendar.VEVENT]

    def getVToDosDB(self):
        return self.mV[PyCalendar.VTODO]

    def getVJournalsDB(self):
        return self.mV[PyCalendar.VJOURNAL]

    def getVFreeBusyDB(self):
        return self.mV[PyCalendar.VFREEBUSY]

    def getVTimezoneDB(self):
        return self.mV[PyCalendar.VTIMEZONE]

    def getAllDBs(self, list):
        
        list.extend(self.mV)

    # Disconnected support
    def getETag(self):
        return self.mETag

    def setETag(self, etag):
        self.mETag = etag

#    def getRecording(self):
#        return self.mRecordDB
#
#    def clearRecording(self):
#        self.mRecordDB.clear()
#
#    def needsSync(self):
#        return not self.mRecordDB.empty()

    #void    ParseCache(istream& is)
    #void    GenerateCache(ostream& os) const

    # Get expanded components
    def getVEvents(self, period, list, all_day_at_top = True):
        # Look at each VEvent
        for vevent in self.mV[PyCalendar.VEVENT]:
            vevent.expandPeriod(period, list)
        
        if (all_day_at_top):
            list.sort(PyCalendarComponentExpanded.sort_by_dtstart_allday)
        else:
            list.sort(PyCalendarComponentExpanded.sort_by_dtstart)
        
    def getVToDos(self, only_due, all_dates, upto_due_date, list):
        # Get current date-time less one day to test for completed events during the last day
        minusoneday = PyCalendarDateTime()
        minusoneday.setNowUTC()
        minusoneday.offsetDay(-1)
    
        today = PyCalendarDateTime()
        today.setToday()
    
        # Look at each VToDo
        for vtodo in self.mV[PyCalendar.VTODO]:

            # Filter out done (that were complted more than a day ago) or cancelled to dos if required
            if only_due:
                if vtodo.getStatus() == definitions.eStatus_VToDo_Cancelled:
                    continue
                elif ((vtodo.getStatus() == definitions.eStatus_VToDo_Completed) and
                            (not vtodo.hasCompleted() or (vtodo.getCompleted() < minusoneday))):
                    continue
    
            # Filter out those with end after chosen date if required
            if not all_dates:
                if vtodo.hasEnd() and (vtodo.getEnd() > upto_due_date):
                    continue
                elif not vtodo.hasEnd() and (today > upto_due_date):
                    continue
    
            list.append(PyCalendarComponentExpandedShared(PyCalendarComponentExpanded(vtodo, None)))
        
    def getRecurrenceInstancesItems(self, type, uid, items):
        # Get instances from list
        self.getComponents(type).getRecurrenceInstancesItems(uid, items)

    def getRecurrenceInstancesIds(self, type, uid, ids):
        # Get instances from list
        self.getComponents(type).getRecurrenceInstancesIds(uid, ids)

    # Freebusy generation
    def getVFreeBusyList(self, period, list):
        # Look at each VFreeBusy
        for vfreebusy in self.mV[PyCalendar.VFREEBUSY]:
            vfreebusy.expandPeriod(period, list)
        
    def getVFreeBusyFB(self, period, fb):
        # First create expanded set
        list = PyCalendarExpandedComponents()
        self.getVEvents(period, list)
        if len(list) == 0:
            return
        
        # Get start/end list for each non-all-day expanded components
        dtstart = []
        dtend = []
        for dt in list:

            # Ignore if all-day
            if dt.getInstanceStart().isDateOnly():
                continue
            
            # Ignore if transparent to free-busy
            transp = ""
            if dt.getOwner().getProperty(definitions.cICalProperty_TRANSP, transp) and (transp == definitions.cICalProperty_TRANSPARENT):
                continue
            
            # Add start/end to list
            dtstart.append(dt.getInstanceStart())
            dtend.append(dt.getInstanceEnd())
        
        # No longer need the expanded items
        list.clear()
    
        # Create non-overlapping periods as properties in the freebusy component
        temp = PyCalendarPeriod(dtstart.front(), dtend.front())
        dtstart_iter = dtstart.iter()
        dtstart_iter.next()
        dtend_iter = dtend.iter()
        dtend_iter.next()
        for i in i:

            # Check for non-overlap
            if dtstart_iter > temp.getEnd():

                # Current period is complete
                fb.addProperty(PyCalendarProperty(definitions.cICalProperty_FREEBUSY, temp))
                
                # Reset period to new range
                temp = PyCalendarPeriod(dtstart_iter, dtend_iter)
            
            # They overlap - check for extended end
            if dtend_iter > temp.getEnd():

                # Extend the end
                temp = PyCalendarPeriod(temp.getStart(), dtend_iter)
        
        # Add remaining period as property
        fb.addProperty(PyCalendarProperty(definitions.cICalProperty_FREEBUSY, temp))

    def getFreeBusy(self, period, fb):
        # First create expanded set

        list = []
        self.getVEvents(period, list)
        
        # Get start/end list for each non-all-day expanded components
        for comp in list:

            # Ignore if all-day
            if comp.getInstanceStart().isDateOnly():
                continue
            
            # Ignore if transparent to free-busy
            transp = ""
            if comp.getOwner().getProperty(definitions.cICalProperty_TRANSP, transp) and (transp == definitions.cICalProperty_TRANSPARENT):
                continue
            
            # Add free busy item to list
            status = comp.getMaster().getStatus()
            if status in (definitions.eStatus_VEvent_None, definitions.eStatus_VEvent_Confirmed):
                fb.append(PyCalendarFreeBusy(PyCalendarFreeBusy.BUSY, PyCalendarPeriod(comp.getInstanceStart(), comp.getInstanceEnd())))
            elif status == definitions.eStatus_VEvent_Tentative:
                fb.append(PyCalendarFreeBusy(PyCalendarFreeBusy.BUSYTENTATIVE, PyCalendarPeriod(comp.getInstanceStart(), comp.getInstanceEnd())))
                break
            elif status == definitions.eStatus_VEvent_Cancelled:
                # Cancelled => does not contribute to busy time
                pass

        # Now get the VFREEBUSY info
        list2 = []
        self.getVFreeBusy(period, list2)
        
        # Get start/end list for each free-busy
        for comp in list2:

            # Expand component and add free busy info to list
            comp.expandPeriod(period, fb)
            
        # Add remaining period as property
        PyCalendarFreeBusy.resolveOverlaps(fb)
    
    # Timezone lookups
    def mergeTimezones(self, cal):
        # Merge each timezone from other calendar
        for tz in  cal.mV[PyCalendar.VTIMEZONE]:

            # See whether matching item is already installed
            if not self.mV[PyCalendar.VTIMEZONE].has_key(tz.getMapKey()):

                # Item does not already exist - so copy and add it
                copy = PyCalendarVTimezone(tz)
                self.mV[PyCalendar.VTIMEZONE].addComponent(copy)

            else:
                # Merge similar items
                self.mV[PyCalendar.VTIMEZONE][tz.getMapKey()].mergeTimezone(tz)
        
    def getTimezoneOffsetSeconds(self, timezone, dt):
        # Find timezone that matches the name (which is the same as the map key)
        if self.mV[PyCalendar.VTIMEZONE].has_key(timezone):
            return self.mV[PyCalendar.VTIMEZONE][timezone].getTimezoneOffsetSeconds(dt)
        else:
            return 0

    def getTimezoneDescriptor(self, timezone, dt):
        # Find timezone that matches the name (which is the same as the map key)
        if self.mV[PyCalendar.VTIMEZONE].has_key(timezone):
            return self.mV[PyCalendar.VTIMEZONE][timezone].getTimezoneDescriptor(dt)
        else:
            return ""

    def getTimezones(self, tzids):
        # Get all timezones in a list for sorting
        sorted = {}
        for tz in self.mV[PyCalendar.VTIMEZONE]:
            sorted.setdefault(tz.getSortKey(), []).append(tz)
    
        # Now add to list in sorted order
        for tzs in sorted.itervalues():
            for tz in tzs:
                tzids.append(tz.getID())
        
    def getTimezone(self, tzid):
        # Find timezone that matches the name (which is the same as the map key)
        if self.mV[PyCalendar.VTIMEZONE].has_key(tzid):
            return self.mV[PyCalendar.VTIMEZONE][tzid]
        else:
            return None

    # Add/remove components
    def changedComponent(self, comp):
        #Calendar has changed
        self.setDirty()
        
        # Record change
        #PyCalendarComponentRecord.recordAction(self.mRecordDB, comp, PyCalendarComponentRecord.eChanged)
        
        # Broadcast change
        #CComponentAction action(CComponentAction::eChanged, *this, *comp)
        #Broadcast_Message(eBroadcast_ChangedComponent, &action)
        

    def addNewVEvent(self, vevent, moved = False):
        # Do not init props if moving
        if not moved:

            # Make sure UID is set and unique
            uid = ""
            vevent.setUID(uid)
            
            # Init DTSTAMP to now
            vevent.initDTSTAMP()
    
        self.mV[PyCalendar.VEVENT].addComponent(vevent)
    
        # Calendar has changed
        self.setDirty()
        
        #Record change
        #PyICalendarComponentRecord.recordAction(self.mRecordDB, vevent, PyCalendarComponentRecord.eAdded)
        
        # Broadcast change
        #action = CComponentAction(CComponentAction.eAdded, self, vevent)
        #Broadcast_Message(eBroadcast_AddedComponent, &action)

    def removeVEvent(self, vevent, delete_it = True):
        # Record change  before delete occurs
        #PyCalendarComponentRecord.recordAction(self.mRecordDB, vevent, PyCalendarComponentRecord.eRemoved)
    
        # Remove from the map (do not delete here - wait until after broadcast)
        self.mVEvent.removeComponent(vevent, False)
        
        # Calendar has changed
        self.setDirty()
        
        # Broadcast change
        #action = CComponentAction(CComponentAction.eRemoved, self, vevent)
        #Broadcast_Message(eBroadcast_RemovedComponent, &action)
        
        # Delete it here after all changes
        if delete_it:
            vevent = None
        
    def removeRecurringVEvent(self, vevent, recur):
        # Determine how to delete
        if recur == PyCalendar.REMOVE_ALL:
            # Remove the top-level master event
            self.removeVEvent(vevent.getTrueMaster())

        elif recur == PyCalendar.REMOVE_ONLY_THIS:
            # Simply exclude this instance from the top-level master vevent -
            # this works even if this instance is the top-level (first) one
            master = vevent.getTrueMaster()

            # NB the vevent will be deleted as part of this so cache the instance start before
            exclude = PyCalendarDateTime(vevent.getInstanceStart())

            # The start instance is the RECURRENCE-ID to exclude
            master.excludeRecurrence(exclude)

            # Tell it it has changed (i.e. bump sequence)
            master.changed()

        elif recur == PyCalendar.REMOVE_THIS_AND_FUTURE:
            # Simply exclude this instance from the master vevent
            master = vevent.getTrueMaster()

            # NB the vevent will be deleted as part of this so cache the instance start before
            exclude = PyCalendarDateTime(vevent.getInstanceStart())

            # The DTSTART specifies the recurrence that we exclude
            master.excludeFutureRecurrence(exclude)

            # Tell it it has changed (i.e. bump sequence)
            master.changed()
        
        # Calendar has changed
        self.setDirty()
        
        # Broadcast change
        #Broadcast_Message(eBroadcast_Edit, this)


    def addNewVToDo(self, vtodo, moved = False):
        # Do not init props if moving
        if not moved:

            # Make sure UID is set and unique
            uid = ""
            vtodo.setUID(uid)
            
            # Init DTSTAMP to now
            vtodo.initDTSTAMP()
        
        self.mVToDo.addComponent(vtodo)
        
        # Calendar has changed
        self.setDirty()
        
        # Record change
        #PyCalendarComponentRecord.recordAction(self.mRecordDB, vtodo, PyCalendarComponentRecord.eAdded)
        
        # Broadcast change
        #action = CComponentAction(CComponentAction.eAdded, self, vtodo)
        #Broadcast_Message(eBroadcast_AddedComponent, &action)
        
    def removeVToDo(self, vtodo, delete_it = True):
        # Record change  before delete occurs
        #PyCalendarComponentRecord.recordAction(self.mRecordDB, vtodo, PyCalendarComponentRecord.eRemoved)
    
        # Remove from the map (do not delete here - wait until after broadcast)
        self.mVToDo.removeComponent(vtodo, False)
        
        # Calendar has changed
        self.setDirty()
        
        # Broadcast change
        #action = CComponentAction(CComponentAction.eRemoved, self, vtodo)
        #Broadcast_Message(eBroadcast_RemovedComponent, &action)
        
        # Delete it here after all changes
        if delete_it:
            vtodo = None

    def findComponent(self, orig, find = FIND_EXACT):
        # Based on original component type. If we have a component of one type with the same UID
        # as a component of another type something is really f*cked up!
        index = self.getComponentIndex(orig.getType())
        if index != -1:
            return self.findComponentDB(self.mV[index], orig, find)
        else:
            return None

    def addComponent(self, comp):
        # Based on original component type. If we have a component of one type with the same UID
        # as a component of another type something is really f*cked up!
        index = self.getComponentIndex(comp.getType())
        if index != -1:
            self.addComponentDB(self.mV[index], comp)
        else:
            comp = None

    def getComponentByKey(self, mapkey):
        
        for compdb in self.mV:
            result = self.getComponentByKeyDB(compdb, mapkey)
            if result is not None:
                return result
        else:
            return None

    def removeComponentByKey(self, mapkey):

        for compdb in self.mV:
            if self.removeComponentByKeyDB(compdb, mapkey):
                return
        

    def isReadOnly(self):
        return self.mReadOnly

    def setReadOnly(self, ro = True):
        self.mReadOnly = ro

    # Change state
    def isDirty(self):
        return self.mDirty

    def setDirty(self, dirty = True):
        self.mDirty = dirty

    def isTotalReplace(self):
        return self.mTotalReplace

    def setTotalReplace(self, replace = True):
        self.mTotalReplace = replace

    def getComponents(self, type):
        return self.mV[self.getComponentIndex(type)]

    def getComponentIndex(self, type):
        if type == PyCalendarComponent.eVEVENT:
            return PyCalendar.VEVENT
        elif type == PyCalendarComponent.eVTODO:
            return PyCalendar.VTODO
        elif type == PyCalendarComponent.eVJOURNAL:
            return PyCalendar.VJOURNAL
        elif type == PyCalendarComponent.eVFREEBUSY:
            return PyCalendar.VFREEBUSY
        elif type == PyCalendarComponent.eVTIMEZONE:
            return PyCalendar.VTIMEZONE
        else:
            return -1

    def addDefaultProperties(self):
        self.addProperty(PyCalendarProperty(definitions.cICalProperty_PRODID, PyCalendar.sProdID))
        self.addProperty(PyCalendarProperty(definitions.cICalProperty_VERSION, "2.0"))
        self.addProperty(PyCalendarProperty(definitions.cICalProperty_CALSCALE, "GREGORIAN"))
        
    def generateDB(self, os, components, for_cache):
        for comp in components:
            comp.generate(os, for_cache)

    def validProperty(self, prop):
        if prop.getName() == definitions.cICalProperty_VERSION:

            tvalue = prop.getTextValue()
            if ((tvalue is None) or (tvalue.getValue() != "2.0")):
                return False

        elif prop.getName() == definitions.cICalProperty_CALSCALE:

            tvalue = prop.getTextValue()
            if ((tvalue is None) or (tvalue.getValue() != "GREGORIAN")):
                return False

        return True
        
    def ignoreProperty(self, prop):
        return prop.getName() in (definitions.cICalProperty_VERSION, definitions.cICalProperty_CALSCALE, definitions.cICalProperty_PRODID)

    def includeTimezones(self):
        # Get timezone names from each component
        tzids = set()
        self.includeTimezonesDB(self.mV[PyCalendar.VEVENT], tzids)
        self.includeTimezonesDB(self.mV[PyCalendar.VTODO], tzids)
        self.includeTimezonesDB(self.mV[PyCalendar.VJOURNAL], tzids)
        self.includeTimezonesDB(self.mV[PyCalendar.VFREEBUSY], tzids)
    
        # Make sure each timezone is in current calendar
        for tzid in tzids:

            tz = self.getTimezone(tzid)
            if tz is None:

                # Find it in the static object
                tz = PyCalendar.sICalendar.getTimezone(tzid)
                if tz is not None:

                    dup = PyCalendarVTimezone(tz)
                    self.mV[PyCalendar.VTIMEZONE].addComponent(dup)
        
    def includeTimezonesDB(self, components, tzids):
        for comp in components:
            comp.getTimezones(tzids)

    def findComponentDB(self, db, orig, find = FIND_EXACT):
        if find == PyCalendar.FIND_EXACT:
            key = orig.getMapKey()
        else:
            key = orig.getMasterKey()

        if db.has_key(key):
            return db[key]
        else:
            return None
        
    def addComponentDB(self, db, comp):
        # Just add it without doing anything as this is a copy being made during sync'ing
        if not db.addComponent(comp):
            comp = None

    def getComponentByKeyDB(self, db, mapkey):

        if db.has_key(mapkey):
            return db[mapkey]
        else:
            return None

    def removeComponentByKeyDB(self, db, mapkey):
        if db.has_key(mapkey):
            db.removeComponent(mapkey, True)
            return True
        else:
            return False

    class SComponentRegister(object):


        def __init__(self, id, type):
            self.mID = id
            self.mType = type

    sComponents = {}
    sEmbeddedComponents = {}

    @staticmethod
    def initComponents():

        if len(PyCalendar.sComponents) == 0:
            PyCalendar.sComponents[PyCalendarVEvent.getVBegin()] = PyCalendar.SComponentRegister(0, PyCalendarComponent.eVEVENT)
            PyCalendar.sComponents[PyCalendarVToDo.getVBegin()] = PyCalendar.SComponentRegister(1, PyCalendarComponent.eVTODO)
            PyCalendar.sComponents[PyCalendarVJournal.getVBegin()] = PyCalendar.SComponentRegister(2, PyCalendarComponent.eVJOURNAL)
            PyCalendar.sComponents[PyCalendarVFreeBusy.getVBegin()] = PyCalendar.SComponentRegister(3, PyCalendarComponent.eVFREEBUSY)
            PyCalendar.sComponents[PyCalendarVTimezone.getVBegin()] = PyCalendar.SComponentRegister(4, PyCalendarComponent.eVTIMEZONE)
    
        if len(PyCalendar.sEmbeddedComponents) == 0:
            PyCalendar.sEmbeddedComponents[PyCalendarVAlarm.getVBegin()] = PyCalendar.SComponentRegister(5, PyCalendarComponent.eVALARM)
            PyCalendar.sEmbeddedComponents[PyCalendarVTimezoneStandard.getVBegin()] = PyCalendar.SComponentRegister(6, PyCalendarComponent.eVTIMEZONE)
            PyCalendar.sEmbeddedComponents[PyCalendarVTimezoneDaylight.getVBegin()] = PyCalendar.SComponentRegister(7, PyCalendarComponent.eVTIMEZONE)

    @staticmethod
    def makeComponent(id, calendar):

        if id == 0:
            return PyCalendarVEvent(calendar=calendar)

        elif id == 1:
            return PyCalendarVToDo(calendar=calendar)

        elif id == 2:
            return PyCalendarVJournal(calendar=calendar)

        elif id == 3:
            return PyCalendarVFreeBusy(calendar=calendar)

        elif id == 4:
            return PyCalendarVTimezone(calendar=calendar)

        elif id == 5:
            return PyCalendarVAlarm(calendar=calendar)

        elif id == 6:
            return PyCalendarVTimezoneStandard(calendar=calendar)

        elif id == 7:
            return PyCalendarVTimezoneDaylight(calendar=calendar)

        else:
            return None

    @staticmethod
    def initDefaultTimezones():
        # Add default timezones to this (static) calendar
        pass

PyCalendar.sICalendar = PyCalendar()
