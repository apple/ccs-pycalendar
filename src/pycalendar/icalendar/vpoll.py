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

from pycalendar.icalendar import definitions
from pycalendar.icalendar import itipdefinitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS

class VPoll(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTAMP,
        definitions.cICalProperty_UID,
        definitions.cICalProperty_ORGANIZER,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_ACCEPT_RESPONSE,
        definitions.cICalProperty_CLASS,
        definitions.cICalProperty_CREATED,
        definitions.cICalProperty_COMPLETED,
        definitions.cICalProperty_DESCRIPTION,
        definitions.cICalProperty_DTSTART,
        definitions.cICalProperty_DTEND,
        definitions.cICalProperty_DURATION,
        definitions.cICalProperty_LAST_MODIFIED,
        definitions.cICalProperty_POLL_MODE,
        definitions.cICalProperty_POLL_PROPERTIES,
        definitions.cICalProperty_PRIORITY,
        definitions.cICalProperty_SEQUENCE,
        definitions.cICalProperty_STATUS,
        definitions.cICalProperty_SUMMARY,
        definitions.cICalProperty_URL,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def getType(self):
        return definitions.cICalComponent_VPOLL


    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VPOLL


    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_DTSTART,
            definitions.cICalProperty_DURATION,
            definitions.cICalProperty_DTEND,
        )

Component.registerComponent(definitions.cICalComponent_VPOLL, VPoll)
