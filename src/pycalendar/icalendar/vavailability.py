##
#    Copyright (c) 2011-2013 Cyrus Daboo. All rights reserved.
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

from pycalendar.icalendar import definitions
from pycalendar.icalendar import itipdefinitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS

class VAvailability(Component):

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
        super(VAvailability, self).__init__(parent=parent)


    def duplicate(self, parent=None):
        return super(VAvailability, self).duplicate(parent=parent)


    def getType(self):
        return definitions.cICalComponent_VAVAILABILITY


    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VAVAILABILITY


    def finalise(self):
        super(VAvailability, self).finalise()


    def validate(self, doFix=False):
        """
        Validate the data in this component and optionally fix any problems, else raise. If
        loggedProblems is not None it must be a C{list} and problem descriptions are appended
        to that.
        """

        fixed, unfixed = super(VAvailability, self).validate(doFix)

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
            super(VAvailability, self).addComponent(comp)
        else:
            raise ValueError


    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_DTSTART,
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_DTEND,
        )


    def getTimezones(self, tzids):
        """
        In addition to looking in the VAVAILABILITY component, we must also return any TZIDs used
        in AVAILABLE child components.

        @param tzids: result to report back
        @type tzids: L{set}
        """

        super(VAvailability, self).getTimezones(tzids)
        for available in self.getComponents(definitions.cICalComponent_AVAILABLE):
            available.getTimezones(tzids)

Component.registerComponent(definitions.cICalComponent_VAVAILABILITY, VAvailability)
