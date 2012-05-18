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

from cStringIO import StringIO
from pycalendar import definitions, xmldefs
from pycalendar.available import PyCalendarAvailable
from pycalendar.componentbase import PyCalendarComponentBase
from pycalendar.componentexpanded import PyCalendarComponentExpanded
from pycalendar.componentrecur import PyCalendarComponentRecur
from pycalendar.datetime import PyCalendarDateTime
from pycalendar.exceptions import PyCalendarInvalidData,\
    PyCalendarValidationError
from pycalendar.freebusy import PyCalendarFreeBusy
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS
from pycalendar.parser import ParserContext
from pycalendar.period import PyCalendarPeriod
from pycalendar.property import PyCalendarProperty
from pycalendar.utils import readFoldedLine
from pycalendar.valarm import PyCalendarVAlarm
from pycalendar.vavailability import PyCalendarVAvailability
from pycalendar.vevent import PyCalendarVEvent
from pycalendar.vfreebusy import PyCalendarVFreeBusy
from pycalendar.vjournal import PyCalendarVJournal
from pycalendar.vtimezone import PyCalendarVTimezone
from pycalendar.vtimezonedaylight import PyCalendarVTimezoneDaylight
from pycalendar.vtimezonestandard import PyCalendarVTimezoneStandard
from pycalendar.vtodo import PyCalendarVToDo
from pycalendar.vunknown import PyCalendarUnknownComponent
import collections
import xml.etree.cElementTree as XML
import json

class PyCalendar(PyCalendarComponentBase):

    REMOVE_ALL = 0
    REMOVE_ONLY_THIS = 1
    REMOVE_THIS_AND_FUTURE = 2

    FIND_EXACT = 0
    FIND_MASTER = 1

    sProdID = "-//mulberrymail.com//Mulberry v4.0//EN"
    sDomain = "mulberrymail.com"

    @staticmethod
    def setPRODID(prodid):
        PyCalendar.sProdID = prodid

    @staticmethod
    def setDomain(domain):
        PyCalendar.sDomain = domain

    propertyCardinality_1 = (
        definitions.cICalProperty_PRODID,
        definitions.cICalProperty_VERSION,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_CALSCALE,
        definitions.cICalProperty_METHOD,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None, add_defaults=True):
        super(PyCalendar, self).__init__(None)

        self.mName = ""
        self.mDescription = ""
        self.mMasterComponentsByTypeAndUID = collections.defaultdict(lambda:collections.defaultdict(list))
        self.mOverriddenComponentsByUID = collections.defaultdict(list)
    
        if add_defaults:
            self.addDefaultProperties()
    
    def duplicate(self):
        other = super(PyCalendar, self).duplicate()
        other.mName = self.mName
        other.mDescription = self.mDescription
        return other

    def getType(self):
        return definitions.cICalComponent_VCALENDAR

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
            if len(name):
                self.ddProperty(PyCalendarProperty(definitions.cICalProperty_XWRCALNAME, name))
            

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
            if len(description):
                self.addProperty(PyCalendarProperty(definitions.cICalProperty_XWRCALDESC, description))

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

    def validate(self, doFix=False, doRaise=False):
        """
        Validate the data in this component and optionally fix any problems. Return
        a tuple containing two lists: the first describes problems that were fixed, the
        second problems that were not fixed. Caller can then decide what to do with unfixed
        issues.
        """
        
        # Optional raise behavior
        fixed, unfixed = super(PyCalendar, self).validate(doFix)
        if doRaise and unfixed:
            raise PyCalendarValidationError(";".join(unfixed))
        return fixed, unfixed

    def sortedComponentNames(self):
        return (
            definitions.cICalComponent_VTIMEZONE,
            definitions.cICalComponent_VEVENT,
            definitions.cICalComponent_VTODO,
            definitions.cICalComponent_VJOURNAL,
            definitions.cICalComponent_VFREEBUSY,
            definitions.cICalComponent_VAVAILABILITY,
        )

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_VERSION,
            definitions.cICalProperty_CALSCALE,
            definitions.cICalProperty_METHOD,
            definitions.cICalProperty_PRODID,
        )

    @staticmethod
    def parseText(data):
        
        cal = PyCalendar(add_defaults=False)
        if cal.parse(StringIO(data)):
            return cal
        else:
            return None

    def parse(self, ins):

        result = False
        
        self.setProperties({})
    
        LOOK_FOR_VCALENDAR = 0
        GET_PROPERTY_OR_COMPONENT = 1
    
        state = LOOK_FOR_VCALENDAR
    
        # Get lines looking for start of calendar
        lines = [None, None]
        comp = self
        compend = None
        componentstack = []
    
        while readFoldedLine(ins, lines):
            
            line = lines[0]

            if state == LOOK_FOR_VCALENDAR:

                # Look for start
                if line == self.getBeginDelimiter():
                    # Next state
                    state = GET_PROPERTY_OR_COMPONENT
    
                    # Indicate success at this point
                    result = True

                # Handle blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise PyCalendarInvalidData("iCalendar data has blank lines")
                
                # Unrecognized data
                else:
                    raise PyCalendarInvalidData("iCalendar data not recognized", line)

            elif state == GET_PROPERTY_OR_COMPONENT:

                # Parse property or look for start of component
                if line.startswith("BEGIN:"):

                    # Push previous details to stack
                    componentstack.append((comp, compend,))

                    # Start a new component
                    comp = PyCalendar.makeComponent(line[6:], comp)
                    compend = comp.getEndDelimiter()

                # Look for end of object
                elif line == self.getEndDelimiter():

                    # Finalise the current calendar
                    self.finalise()
    
                    # Change state
                    state = LOOK_FOR_VCALENDAR

                # Look for end of current component
                elif line == compend:

                    # Finalise the component (this caches data from the properties)
                    comp.finalise()
    
                    # Embed component in parent and reset to use parent
                    componentstack[-1][0].addComponent(comp)
                    comp, compend = componentstack.pop()
                
                # Blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise PyCalendarInvalidData("iCalendar data has blank lines")

                # Must be a property
                else:

                    # Parse attribute/value for top-level calendar item
                    prop = PyCalendarProperty()
                    if prop.parse(line):

                        # Check for valid property
                        if comp is self:
                            if not comp.validProperty(prop):
                                raise PyCalendarInvalidData("Invalid property", str(prop))
                            elif not comp.ignoreProperty(prop):
                                comp.addProperty(prop)
                        else:
                            comp.addProperty(prop)
    
        # Check for truncated data
        if state != LOOK_FOR_VCALENDAR:
            raise PyCalendarInvalidData("iCalendar data not complete")
            
        # We need to store all timezones in the static object so they can be accessed by any date object
        from timezonedb import PyCalendarTimezoneDatabase
        PyCalendarTimezoneDatabase.mergeTimezones(self, self.getComponents(definitions.cICalComponent_VTIMEZONE))
    
        # Validate some things
        if result and not self.hasProperty("VERSION"):
            raise PyCalendarInvalidData("iCalendar missing VERSION")

        return result
    
    def parseComponent(self, ins):
        
        result = None
    
        LOOK_FOR_VCALENDAR = 0
        GET_PROPERTY_OR_COMPONENT = 1
        GOT_VCALENDAR = 4
    
        state = LOOK_FOR_VCALENDAR
    
        # Get lines looking for start of calendar
        lines = [None, None]
        comp = self
        compend = None
        componentstack = []
        got_timezone = False
    
        while readFoldedLine(ins, lines):

            if state == LOOK_FOR_VCALENDAR:

                # Look for start
                if lines[0] == self.getBeginDelimiter():
                    # Next state
                    state = GET_PROPERTY_OR_COMPONENT

                # Handle blank line
                elif len(lines[0]) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise PyCalendarInvalidData("iCalendar data has blank lines")
                
                # Unrecognized data
                else:
                    raise PyCalendarInvalidData("iCalendar data not recognized", lines[0])

            elif state == GET_PROPERTY_OR_COMPONENT:

                # Parse property or look for start of component
                if lines[0].startswith("BEGIN:"):

                    # Push previous details to stack
                    componentstack.append((comp, compend,))

                    # Start a new component
                    comp = PyCalendar.makeComponent(lines[0][6:], comp)
                    compend = comp.getEndDelimiter()
                    
                    # Cache as result - but only the first one, we ignore the rest
                    if result is None:
                        result = comp
    
                    # Look for timezone component to trigger timezone merge only if one is present
                    if comp.getType() == definitions.cICalComponent_VTIMEZONE:
                        got_timezone = True

                elif lines[0] == self.getEndDelimiter():

                    # Change state
                    state = GOT_VCALENDAR

                # Look for end of current component
                elif lines[0] == compend:

                    # Finalise the component (this caches data from the properties)
                    comp.finalise()
    
                    # Embed component in parent and reset to use parent
                    componentstack[-1][0].addComponent(comp)
                    comp, compend = componentstack.pop()
                
                # Blank line
                elif len(lines[0]) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise PyCalendarInvalidData("iCalendar data has blank lines")

                # Ignore top-level items
                elif comp is self:
                    pass

                # Must be a property
                else:

                    # Parse attribute/value for top-level calendar item
                    prop = PyCalendarProperty()
                    if prop.parse(lines[0]):

                        # Check for valid property
                        if comp is not self:
                            comp.addProperty(prop)
            
            # Exit if we have one - ignore all the rest
            if state == GOT_VCALENDAR:
                break
    
        # We need to store all timezones in the static object so they can be accessed by any date object
        # Only do this if we read in a timezone
        if got_timezone:
            from timezonedb import PyCalendarTimezoneDatabase
            PyCalendarTimezoneDatabase.mergeTimezones(self, self.getComponents(definitions.cICalComponent_VTIMEZONE))
    
        return result
        
    def addComponent(self, component):
        """
        Override to track components by UID.
        """
        super(PyCalendar, self).addComponent(component)
        
        if isinstance(component, PyCalendarComponentRecur):
            uid = component.getUID()
            rid = component.getRecurrenceID()
            if rid:
                self.mOverriddenComponentsByUID[uid].append(component)
            else:
                self.mMasterComponentsByTypeAndUID[component.getType()][uid] = component

    def removeComponent(self, component):
        """
        Override to track components by UID.
        """
        super(PyCalendar, self).removeComponent(component)

        if isinstance(component, PyCalendarComponentRecur):
            uid = component.getUID()
            rid = component.getRecurrenceID()
            if rid:
                self.mOverriddenComponentsByUID[uid].remove(component)
            else:
                del self.mMasterComponentsByTypeAndUID[component.getType()][uid]

    def getText(self, includeTimezones=False):
        s = StringIO()
        self.generate(s, includeTimezones=includeTimezones)
        return s.getvalue()

    def generate(self, os, includeTimezones=False):
        # Make sure all required timezones are in this object
        if includeTimezones:
            self.includeTimezones()
        super(PyCalendar, self).generate(os)
        
    def getTextXML(self, includeTimezones=False):
        node = self.writeXML(includeTimezones)
        return xmldefs.toString(node)

    def writeXML(self, includeTimezones=False):
        # Make sure all required timezones are in this object
        if includeTimezones:
            self.includeTimezones()
            
        # Root node structure
        root = XML.Element(xmldefs.makeTag(xmldefs.iCalendar20_namespace, xmldefs.icalendar))
        super(PyCalendar, self).writeXML(root, xmldefs.iCalendar20_namespace)
        return root
        
    def getTextJSON(self, includeTimezones=False):
        jobject = self.writeJSON(includeTimezones)
        return json.dumps(jobject, indent=2)

    def writeJSON(self, includeTimezones=False):
        # Make sure all required timezones are in this object
        if includeTimezones:
            self.includeTimezones()
            
        # Root node structure
        vcalendar = []
        super(PyCalendar, self).writeJSON(vcalendar)
        return vcalendar[0]
        
    # Get expanded components
    def getVEvents(self, period, list, all_day_at_top = True):
        # Look at each VEvent
        for vevent in self.getComponents(definitions.cICalComponent_VEVENT):
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
        for vtodo in self.getComponents(definitions.cICalComponent_VTODO):

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
    
            # TODO: fix this
            #list.append(PyCalendarComponentExpandedShared(PyCalendarComponentExpanded(vtodo, None)))
        
    def getRecurrenceInstancesItems(self, type, uid, items):
        # Get instances from list
        items.extend(self.mOverriddenComponentsByUID.get(uid, ()))

    def getRecurrenceInstancesIds(self, type, uid, ids):
        # Get instances from list
        ids.extend([comp.getRecurrenceID() for comp in self.mOverriddenComponentsByUID.get(uid, ())])

    # Freebusy generation
    def getVFreeBusyList(self, period, list):
        # Look at each VFreeBusy
        for vfreebusy in self.getComponents(definitions.cICalComponent_VFREEBUSY):
            vfreebusy.expandPeriod(period, list)
        
    def getVFreeBusyFB(self, period, fb):
        # First create expanded set
        # TODO: fix this
        #list = PyCalendarExpandedComponents()
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
    
    def getTimezoneOffsetSeconds(self, tzid, dt):
        # Find timezone that matches the name (which is the same as the map key)
        timezone = self.getTimezone(tzid)
        return timezone.getTimezoneOffsetSeconds(dt) if timezone else 0

    def getTimezoneDescriptor(self, tzid, dt):
        # Find timezone that matches the name (which is the same as the map key)
        timezone = self.getTimezone(tzid)
        return timezone.getTimezoneDescriptor(dt) if timezone else ""

    def getTimezone(self, tzid):
        # Find timezone that matches the name (which is the same as the map key)
        for timezone in self.getComponents(definitions.cICalComponent_VTIMEZONE):
            if timezone.getID() == tzid:
                return timezone
        else:
            return None

    def addDefaultProperties(self):
        self.addProperty(PyCalendarProperty(definitions.cICalProperty_PRODID, PyCalendar.sProdID))
        self.addProperty(PyCalendarProperty(definitions.cICalProperty_VERSION, "2.0"))
        self.addProperty(PyCalendarProperty(definitions.cICalProperty_CALSCALE, "GREGORIAN"))
        
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
        return False #prop.getName() in (definitions.cICalProperty_VERSION, definitions.cICalProperty_CALSCALE, definitions.cICalProperty_PRODID)

    def includeTimezones(self):
        # Get timezone names from each component
        tzids = set()
        for component in self.mComponents:
            if component.getType() != definitions.cICalComponent_VTIMEZONE:
                component.getTimezones(tzids)
    
        # Make sure each timezone is in current calendar
        from timezonedb import PyCalendarTimezoneDatabase
        for tzid in tzids:
            tz = self.getTimezone(tzid)
            if tz is None:
                # Find it in the static object
                tz = PyCalendarTimezoneDatabase.getTimezone(tzid)
                if tz is not None:
                    dup = tz.duplicate()
                    self.addComponent(dup)
        
    @staticmethod
    def makeComponent(compname, parent):

        mapper = {
            definitions.cICalComponent_VEVENT:PyCalendarVEvent,
            definitions.cICalComponent_VTODO:PyCalendarVToDo,
            definitions.cICalComponent_VJOURNAL:PyCalendarVJournal,
            definitions.cICalComponent_VFREEBUSY:PyCalendarVFreeBusy,
            definitions.cICalComponent_VTIMEZONE:PyCalendarVTimezone,
            definitions.cICalComponent_VAVAILABILITY:PyCalendarVAvailability,
            definitions.cICalComponent_VALARM:PyCalendarVAlarm,
            definitions.cICalComponent_AVAILABLE:PyCalendarAvailable,
            definitions.cICalComponent_STANDARD:PyCalendarVTimezoneStandard,
            definitions.cICalComponent_DAYLIGHT:PyCalendarVTimezoneDaylight,
        }
        
        try:
            cls = mapper[compname]
            return cls(parent=parent)
        except KeyError:
            return PyCalendarUnknownComponent(parent=parent, comptype=compname)
