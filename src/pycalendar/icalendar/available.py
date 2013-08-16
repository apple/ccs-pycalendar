##
#    Copyright (c) 2011-2012 Cyrus Daboo. All rights reserved.
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
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.componentrecur import ComponentRecur
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS

class Available(ComponentRecur):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTAMP,
        definitions.cICalProperty_DTSTART,
        definitions.cICalProperty_UID,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_CREATED,
        definitions.cICalProperty_DESCRIPTION,
        definitions.cICalProperty_GEO,
        definitions.cICalProperty_LAST_MODIFIED,
        definitions.cICalProperty_LOCATION,
        definitions.cICalProperty_RECURRENCE_ID,
        definitions.cICalProperty_RRULE,
        definitions.cICalProperty_SEQUENCE,
        definitions.cICalProperty_SUMMARY,
        definitions.cICalProperty_DTEND,
        definitions.cICalProperty_DURATION,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):
        super(Available, self).__init__(parent=parent)


    def duplicate(self, parent=None):
        return super(Available, self).duplicate(parent=parent)


    def getType(self):
        return definitions.cICalComponent_AVAILABLE


    def validate(self, doFix=False):
        """
        Validate the data in this component and optionally fix any problems, else raise. If
        loggedProblems is not None it must be a C{list} and problem descriptions are appended
        to that.
        """

        fixed, unfixed = super(Available, self).validate(doFix)

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


    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_RECURRENCE_ID,
            definitions.cICalProperty_DTSTART,
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_DTEND,
        )
Component.registerComponent(definitions.cICalComponent_AVAILABLE, Available)
