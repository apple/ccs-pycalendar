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

from cStringIO import StringIO
from pycalendar import xmlutils
from pycalendar.containerbase import ContainerBase
from pycalendar.datetime import DateTime
from pycalendar.exceptions import InvalidData
from pycalendar.icalendar import definitions, xmldefinitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.componentexpanded import ComponentExpanded
from pycalendar.icalendar.componentrecur import ComponentRecur
from pycalendar.icalendar.freebusy import FreeBusy
from pycalendar.icalendar.property import Property
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS
from pycalendar.parser import ParserContext
from pycalendar.period import Period
from pycalendar.utils import readFoldedLine
import collections
import json
import xml.etree.cElementTree as XML


class Calendar(ContainerBase):

    REMOVE_ALL = 0
    REMOVE_ONLY_THIS = 1
    REMOVE_THIS_AND_FUTURE = 2

    FIND_EXACT = 0
    FIND_MASTER = 1

    # Enums for includeTimezone parameter
    ALL_TIMEZONES = 0       # Always include referenced timezones
    NONSTD_TIMEZONES = 1    # Only include non-standard referenced timezones
    NO_TIMEZONES = 2        # Never include timezones other than those already present

    sContainerDescriptor = "iCalendar"
    sComponentType = Component
    sPropertyType = Property

    sFormatText = "text/calendar"
    sFormatJSON = "application/calendar+json"

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
        super(Calendar, self).__init__(add_defaults=add_defaults)

        self.mName = ""
        self.mDescription = ""
        self.mMasterComponentsByTypeAndUID = collections.defaultdict(lambda: collections.defaultdict(list))
        self.mOverriddenComponentsByUID = collections.defaultdict(list)

    def __str__(self):
        """
        Override this to generate text without adding timezones - i.e., this will not change the
        underlying object in any way.
        """
        return self.getText(includeTimezones=Calendar.NO_TIMEZONES)

    def duplicate(self):
        other = super(Calendar, self).duplicate()
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
                self.ddProperty(Property(definitions.cICalProperty_XWRCALNAME, name))

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
                self.addProperty(Property(definitions.cICalProperty_XWRCALDESC, description))

    def getMethod(self):
        result = ""
        if self.hasProperty(definitions.cICalProperty_METHOD):
            result = self.loadValueString(definitions.cICalProperty_METHOD)
        return result

    def changeUID(self, oldUID, newUID):
        """
        Change the UID of all components with a matching UID to a new value. We need to
        do this at the calendar level because this object maintains mappings based on UID
        which need to be updated whenever the UID changes.

        @param oldUID: the old value to match
        @type oldUID: C{str}
        @param newUID: the new value to match
        @type newUID: C{str}
        """

        # Each component
        for component in self.mComponents:
            if component.getUID() == oldUID:
                component.setUID(newUID)

        # Maps
        if oldUID in self.mOverriddenComponentsByUID:
            self.mOverriddenComponentsByUID[newUID] = self.mOverriddenComponentsByUID[oldUID]
            del self.mOverriddenComponentsByUID[oldUID]
        for ctype in self.mMasterComponentsByTypeAndUID:
            if oldUID in self.mMasterComponentsByTypeAndUID[ctype]:
                self.mMasterComponentsByTypeAndUID[ctype][newUID] = self.mMasterComponentsByTypeAndUID[ctype][oldUID]
                del self.mMasterComponentsByTypeAndUID[ctype][oldUID]

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

    def parse(self, ins):

        result = super(Calendar, self).parse(ins)

        # We need to store all timezones in the static object so they can be accessed by any date object
        from pycalendar.timezonedb import TimezoneDatabase
        TimezoneDatabase.mergeTimezones(self, self.getComponents(definitions.cICalComponent_VTIMEZONE))

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

            line = lines[0]

            if state == LOOK_FOR_VCALENDAR:

                # Look for start
                if line == self.getBeginDelimiter():
                    # Next state
                    state = GET_PROPERTY_OR_COMPONENT

                # Handle blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise InvalidData("iCalendar data has blank lines")

                # Unrecognized data
                else:
                    raise InvalidData("iCalendar data not recognized", line)

            elif state == GET_PROPERTY_OR_COMPONENT:

                # Parse property or look for start of component
                if line.startswith("BEGIN:"):

                    # Push previous details to stack
                    componentstack.append((comp, compend,))

                    # Start a new component
                    comp = self.sComponentType.makeComponent(line[6:], comp)
                    compend = comp.getEndDelimiter()

                    # Cache as result - but only the first one, we ignore the rest
                    if result is None:
                        result = comp

                    # Look for timezone component to trigger timezone merge only if one is present
                    if comp.getType() == definitions.cICalComponent_VTIMEZONE:
                        got_timezone = True

                elif line == self.getEndDelimiter():

                    # Change state
                    state = GOT_VCALENDAR

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
                        raise InvalidData("iCalendar data has blank lines")

                # Ignore top-level items
                elif comp is self:
                    pass

                # Must be a property
                else:

                    # Parse parameter/value for top-level calendar item
                    prop = self.sPropertyType.parseText(line)

                    # Check for valid property
                    if comp is not self:
                        comp.addProperty(prop)

            # Exit if we have one - ignore all the rest
            if state == GOT_VCALENDAR:
                break

        # We need to store all timezones in the static object so they can be accessed by any date object
        # Only do this if we read in a timezone
        if got_timezone:
            from pycalendar.timezonedb import TimezoneDatabase
            TimezoneDatabase.mergeTimezones(self, self.getComponents(definitions.cICalComponent_VTIMEZONE))

        return result

    def addComponent(self, component):
        """
        Override to track components by UID.
        """
        super(Calendar, self).addComponent(component)

        if isinstance(component, ComponentRecur):
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
        super(Calendar, self).removeComponent(component)

        if isinstance(component, ComponentRecur):
            uid = component.getUID()
            rid = component.getRecurrenceID()
            if rid:
                self.mOverriddenComponentsByUID[uid].remove(component)
            else:
                del self.mMasterComponentsByTypeAndUID[component.getType()][uid]

    def deriveComponent(self, recurrenceID):
        """
        Derive an overridden component for the associated RECURRENCE-ID. This assumes
        that the R-ID is valid for the actual recurrence being used.

        @param recurrenceID: the recurrence instance
        @type recurrenceID: L{DateTime}

        @return: the derived component
        @rtype: L{ComponentRecur} or L{None}
        """
        master = self.masterComponent()
        if master is None:
            return None

        # Create the derived instance
        newcomp = master.duplicate()

        # Strip out unwanted recurrence properties
        for propname in (
            definitions.cICalProperty_RRULE,
            definitions.cICalProperty_RDATE,
            definitions.cICalProperty_EXRULE,
            definitions.cICalProperty_EXDATE,
            definitions.cICalProperty_RECURRENCE_ID,
        ):
            newcomp.removeProperties(propname)

        # New DTSTART is the RECURRENCE-ID we are deriving but adjusted to the
        # original DTSTART's localtime
        dtstart = newcomp.getStart()
        dtend = newcomp.getEnd()
        oldduration = dtend - dtstart

        newdtstartValue = recurrenceID.duplicate()
        if not dtstart.isDateOnly():
            if dtstart.local():
                newdtstartValue.adjustTimezone(dtstart.getTimezone())
        else:
            newdtstartValue.setDateOnly(True)

        newcomp.removeProperties(definitions.cICalProperty_DTSTART)
        newcomp.removeProperties(definitions.cICalProperty_DTEND)
        prop = Property(definitions.cICalProperty_DTSTART, newdtstartValue)
        newcomp.addProperty(prop)
        if not newcomp.useDuration():
            prop = Property(definitions.cICalProperty_DTEND, newdtstartValue + oldduration)
            newcomp.addProperty(prop)

        newcomp.addProperty(Property("RECURRENCE-ID", newdtstartValue))

        # After creating/changing a component we need to do this to keep PyCalendar happy
        newcomp.finalise()

        return newcomp

    def masterComponent(self):
        """
        Return the first sub-component of a recurring type that represents the master
        instance.

        @return: the master component
        @rtype: L{ComponentRecur} or L{None}
        """
        for component in self.getComponents():
            if isinstance(component, ComponentRecur):
                rid = component.getRecurrenceID()
                if rid is None:
                    return component
        else:
            return None

    def getText(self, includeTimezones=None, format=None):

        if format is None or format == self.sFormatText:
            s = StringIO()
            self.generate(s, includeTimezones=includeTimezones)
            return s.getvalue()
        elif format == self.sFormatJSON:
            return self.getTextJSON(includeTimezones=includeTimezones)

    def generate(self, os, includeTimezones=None):
        # Make sure all required timezones are in this object
        self.includeMissingTimezones(includeTimezones=includeTimezones)
        super(Calendar, self).generate(os)

    def getTextXML(self, includeTimezones=None):
        node = self.writeXML(includeTimezones)
        return xmlutils.toString(node)

    def writeXML(self, includeTimezones=None):
        # Make sure all required timezones are in this object
        self.includeMissingTimezones(includeTimezones=includeTimezones)

        # Root node structure
        root = XML.Element(xmlutils.makeTag(xmldefinitions.iCalendar20_namespace, xmldefinitions.icalendar))
        super(Calendar, self).writeXML(root, xmldefinitions.iCalendar20_namespace)
        return root

    def getTextJSON(self, includeTimezones=None, sort_keys=False):
        jobject = []
        self.writeJSON(jobject, includeTimezones)
        return json.dumps(jobject[0], indent=2, separators=(',', ':'), sort_keys=sort_keys)

    def writeJSON(self, jobject, includeTimezones=None):
        # Make sure all required timezones are in this object
        self.includeMissingTimezones(includeTimezones=includeTimezones)

        # Root node structure
        super(Calendar, self).writeJSON(jobject)

    # Get expanded components
    def getVEvents(self, period, list, all_day_at_top=True):
        # Look at each VEvent
        for vevent in self.getComponents(definitions.cICalComponent_VEVENT):
            vevent.expandPeriod(period, list)

        if (all_day_at_top):
            list.sort(ComponentExpanded.sort_by_dtstart_allday)
        else:
            list.sort(ComponentExpanded.sort_by_dtstart)

    def getVToDos(self, only_due, all_dates, upto_due_date, list):
        # Get current date-time less one day to test for completed events during the last day
        minusoneday = DateTime()
        minusoneday.setNowUTC()
        minusoneday.offsetDay(-1)

        today = DateTime()
        today.setToday()

        # Look at each VToDo
        for vtodo in self.getComponents(definitions.cICalComponent_VTODO):

            # Filter out done (that were complted more than a day ago) or cancelled to dos if required
            if only_due:
                if vtodo.getStatus() == definitions.eStatus_VToDo_Cancelled:
                    continue
                elif (
                    (vtodo.getStatus() == definitions.eStatus_VToDo_Completed) and
                    (not vtodo.hasCompleted() or (vtodo.getCompleted() < minusoneday))
                ):
                    continue

            # Filter out those with end after chosen date if required
            if not all_dates:
                if vtodo.hasEnd() and (vtodo.getEnd() > upto_due_date):
                    continue
                elif not vtodo.hasEnd() and (today > upto_due_date):
                    continue

            # TODO: fix this
            # list.append(ComponentExpandedShared(ComponentExpanded(vtodo, None)))

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
        # list = ExpandedComponents()
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
        temp = Period(dtstart.front(), dtend.front())
        dtstart_iter = dtstart.iter()
        next(dtstart_iter)
        dtend_iter = dtend.iter()
        next(dtend_iter)
        for _ignore in (None,):

            # Check for non-overlap
            if dtstart_iter > temp.getEnd():

                # Current period is complete
                fb.addProperty(Property(definitions.cICalProperty_FREEBUSY, temp))

                # Reset period to new range
                temp = Period(dtstart_iter, dtend_iter)

            # They overlap - check for extended end
            if dtend_iter > temp.getEnd():

                # Extend the end
                temp = Period(temp.getStart(), dtend_iter)

        # Add remaining period as property
        fb.addProperty(Property(definitions.cICalProperty_FREEBUSY, temp))

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
                fb.append(FreeBusy(FreeBusy.BUSY, Period(comp.getInstanceStart(), comp.getInstanceEnd())))
            elif status == definitions.eStatus_VEvent_Tentative:
                fb.append(FreeBusy(FreeBusy.BUSYTENTATIVE, Period(comp.getInstanceStart(), comp.getInstanceEnd())))
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
        FreeBusy.resolveOverlaps(fb)

    def getTimezoneOffsetSeconds(self, tzid, dt, relative_to_utc=False):
        # Find timezone that matches the name (which is the same as the map key)
        timezone = self.getTimezone(tzid)
        return timezone.getTimezoneOffsetSeconds(dt, relative_to_utc) if timezone else 0

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
        self.addProperty(Property(definitions.cICalProperty_PRODID, Calendar.sProdID))
        self.addProperty(Property(definitions.cICalProperty_VERSION, "2.0"))
        self.addProperty(Property(definitions.cICalProperty_CALSCALE, "GREGORIAN"))

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

    def includeMissingTimezones(self, includeTimezones=None):
        """
        For each timezone referenced in this L{Calendar}, if the corresponding VTIMEZONE component
        is not present, then add the matching component from the timezone database. L{includeTimezones}
        indicates what set of timezones should be automatically included. If set to L{None} the default
        is L{Calendar.NO_TIMEZONES}. Otherwise, one of L{Calendar.ALL_TIMEZONES}, L{Calendar.NONSTD_TIMEZONES},
        or L{Calendar.NO_TIMEZONES} must be used.

        @param includeTimezones: indicated whether all, only non-standard or no timezones are included
        @type includeTimezones: L{int} or L{None}
        """

        # Don't add anything in this case
        if includeTimezones == Calendar.NO_TIMEZONES:
            return
        if includeTimezones is None:
            includeTimezones = Calendar.NONSTD_TIMEZONES

        # Get timezone names from each component
        tzids = set()
        for component in self.mComponents:
            if component.getType() != definitions.cICalComponent_VTIMEZONE:
                component.getTimezones(tzids)

        # Make sure each timezone is in current calendar
        from pycalendar.timezonedb import TimezoneDatabase
        for tzid in tzids:
            # Skip standard timezones if requested
            if includeTimezones == Calendar.NONSTD_TIMEZONES and TimezoneDatabase.isStandardTimezone(tzid):
                continue
            tz = self.getTimezone(tzid)
            if tz is None:
                # Find it in the static object
                tz = TimezoneDatabase.getTimezone(tzid)
                if tz is not None:
                    dup = tz.duplicate()
                    self.addComponent(dup)

    def stripStandardTimezones(self):
        """
        Remove VTIMEZONE components from this L{Calendar} if the corresponding TZIDs are
        in the timezone database.

        @return: L{True} if changes were made, L{False} otherwise
        @rtype: L{bool}
        """
        from pycalendar.timezonedb import TimezoneDatabase
        changed = False
        for component in self.getComponents(definitions.cICalComponent_VTIMEZONE):
            tz = TimezoneDatabase.getTimezone(component.getID())
            if tz is not None and TimezoneDatabase.isStandardTimezone(component.getID()):
                self.removeComponent(component)
                changed = True

        return changed
