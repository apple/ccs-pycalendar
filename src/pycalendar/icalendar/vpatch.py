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
from pycalendar.icalendar.patch import Patch


class VPatch(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_DTSTAMP,
        definitions.cICalProperty_UID,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_PATCH_VERSION,
        definitions.cICalProperty_PATCH_ORDER,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def getType(self):
        return definitions.cICalComponent_VPATCH

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VPATCH

    def sortedComponents(self):
        components = self.mComponents[:]

        def _sortKey(subcomponent):
            if isinstance(subcomponent, Patch):
                return str(len(subcomponent.getPropertyString(definitions.cICalProperty_PATCH_TARGET).split("/")))
            else:
                return subcomponent.getType().upper()

        return sorted(components, key=_sortKey)

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_UID,
            definitions.cICalProperty_PATCH_VERSION,
            definitions.cICalProperty_PATCH_ORDER,
        )

    def addDefaultProperties(self):
        self.setUID()
        self.initDTSTAMP()

Component.registerComponent(definitions.cICalComponent_VPATCH, VPatch)
