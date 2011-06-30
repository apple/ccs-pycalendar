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
from pycalendar.componentrecur import PyCalendarComponentRecur
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS
from pycalendar.property import PyCalendarProperty

class PyCalendarVEvent(PyCalendarComponentRecur):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTAMP,
        definitions.cICalProperty_UID,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_CLASS,
        definitions.cICalProperty_CREATED,
        definitions.cICalProperty_DESCRIPTION,
        definitions.cICalProperty_GEO,
        definitions.cICalProperty_LAST_MODIFIED,
        definitions.cICalProperty_LOCATION,
        definitions.cICalProperty_ORGANIZER,
        definitions.cICalProperty_PRIORITY,
        definitions.cICalProperty_SEQUENCE,
        definitions.cICalProperty_STATUS,
        definitions.cICalProperty_SUMMARY,
        definitions.cICalProperty_TRANSP,
        definitions.cICalProperty_URL,
        definitions.cICalProperty_RECURRENCE_ID,
        definitions.cICalProperty_RRULE,
        definitions.cICalProperty_DTEND,
        definitions.cICalProperty_DURATION,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):
        super(PyCalendarVEvent, self).__init__(parent=parent)
        self.mStatus = definitions.eStatus_VEvent_None

    def duplicate(self, parent=None):
        other = super(PyCalendarVEvent, self).duplicate(parent=parent)
        other.mStatus = self.mStatus
        return other

    def getType(self):
        return definitions.cICalComponent_VEVENT

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VEVENT

    def addComponent(self, comp):
        # We can embed the alarm components only
        if comp.getType() == definitions.cICalComponent_VALARM:
            super(PyCalendarVEvent, self).addComponent(comp)
        else:
            raise ValueError

    def getStatus(self):
        return self.mStatus

    def setStatus(self, status):
        self.mStatus = status

    def finalise(self):
        # Do inherited
        super(PyCalendarVEvent, self).finalise()

        temp = self.loadValueString(definitions.cICalProperty_STATUS)
        if temp is not None:
            if temp == definitions.cICalProperty_STATUS_TENTATIVE:
                self.mStatus = definitions.eStatus_VEvent_Tentative
            elif temp == definitions.cICalProperty_STATUS_CONFIRMED:
                self.mStatus = definitions.eStatus_VEvent_Confirmed
            elif temp == definitions.cICalProperty_STATUS_CANCELLED:
                self.mStatus = definitions.eStatus_VEvent_Cancelled

    def validate(self, doFix=False):
        """
        Validate the data in this component and optionally fix any problems, else raise. If
        loggedProblems is not None it must be a C{list} and problem descriptions are appended
        to that. 
        """
        
        fixed, unfixed = super(PyCalendarVEvent, self).validate(doFix)

        # Extra constraint: if METHOD not present, DTSTART must be
        if self.mParentComponent and not self.mParentComponent.hasProperty(definitions.cICalProperty_METHOD):
            if not self.hasProperty(definitions.cICalProperty_DTSTART):
                # Cannot fix a missing required property
                logProblem = "[%s] Missing required property: %s" % (self.getType(), definitions.cICalProperty_DTSTART,)
                unfixed.append(logProblem)
        
        # Extra constraint: only one of DTEND or DURATION
        if self.hasProperty(definitions.cICalProperty_DTEND) and self.hasProperty(definitions.cICalProperty_DURATION):
            # Fix by removing the DTEND
            logProblem = "[%s] Properties must not both be present: %s, %s" % (
                self.getType(),
                definitions.cICalProperty_DTEND,
                definitions.cICalProperty_DURATION,
            )
            if doFix:
                self.removeProperties(definitions.cICalProperty_DTEND)
                fixed.append(logProblem)
            else:
                unfixed.append(logProblem)
        
        return fixed, unfixed
                
    # Editing
    def editStatus(self, status):
        # Only if it is different
        if self.mStatus != status:
            # Updated cached values
            self.mStatus = status

            # Remove existing STATUS items
            self.removeProperties(definitions.cICalProperty_STATUS)

            # Now create properties
            value = None
            if status == definitions.eStatus_VEvent_None:
                pass
            elif status == definitions.eStatus_VEvent_Tentative:
                value = definitions.cICalProperty_STATUS_TENTATIVE
            elif status == definitions.eStatus_VEvent_Confirmed:
                value = definitions.cICalProperty_STATUS_CONFIRMED
            elif status == definitions.eStatus_VEvent_Cancelled:
                value = definitions.cICalProperty_STATUS_CANCELLED
            else:
                pass

            if value is not None:
                prop = PyCalendarProperty(definitions.cICalProperty_STATUS, value)
                self.addProperty(prop)

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_RECURRENCE_ID,
            definitions.cICalProperty_DTSTART,
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_DTEND,
        )
