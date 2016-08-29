##
#    Copyright (c) 2007-2015 Cyrus Daboo. All rights reserved.
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


class VPatch(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTAMP,
        definitions.cICalProperty_UID,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_PATCH_ORDER,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def getType(self):
        return definitions.cICalComponent_VPATCH

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VPATCH

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_PATCH_ORDER,
        )

    sortOrder = {
        definitions.cICalComponent_ADD: 0,
        definitions.cICalComponent_UPDATE: 1,
        definitions.cICalComponent_REMOVE: 2
    }

    def sortedComponents(self):
        components = self.mComponents[:]

        def _sortKey(subcomponent):
            return VPatch.sortOrder.get(subcomponent.getType().upper(), 3)

        return sorted(components, key=_sortKey)


Component.registerComponent(definitions.cICalComponent_VPATCH, VPatch)
