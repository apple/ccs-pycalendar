##
#    Copyright (c) 2011 Cyrus Daboo. All rights reserved.
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
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS

class PyCalendarVAvailability(PyCalendarComponent):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTAMP,
        definitions.cICalProperty_UID,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_BUSYTYPE,
        definitions.cICalProperty_CLASS,
        definitions.cICalProperty_CREATED,
        definitions.cICalProperty_DESCRIPTION,
        definitions.cICalProperty_DTSTART,
        definitions.cICalProperty_LAST_MODIFIED,
        definitions.cICalProperty_ORGANIZER,
        definitions.cICalProperty_SEQUENCE,
        definitions.cICalProperty_SUMMARY,
        definitions.cICalProperty_URL,
        definitions.cICalProperty_RECURRENCE_ID,
        definitions.cICalProperty_DTEND,
        definitions.cICalProperty_DURATION,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):
        super(PyCalendarVAvailability, self).__init__(parent=parent)

    def duplicate(self, parent=None):
        return super(PyCalendarVAvailability, self).duplicate(parent=parent)

    def getType(self):
        return definitions.cICalComponent_VAVAILABILITY

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VAVAILABILITY

    def finalise(self):
        super(PyCalendarVAvailability, self).finalise()

    def validate(self, doFix=False):
        """
        Validate the data in this component and optionally fix any problems, else raise. If
        loggedProblems is not None it must be a C{list} and problem descriptions are appended
        to that. 
        """
        
        fixed, unfixed = super(PyCalendarVAvailability, self).validate(doFix)

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
                
    def addComponent(self, comp):
        # We can embed the available components only
        if comp.getType() == definitions.cICalComponent_AVAILABLE:
            super(PyCalendarVAvailability, self).addComponent(comp)
        else:
            raise ValueError

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_DTSTART,
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_DTEND,
        )
