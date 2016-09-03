##
#    Copyright (c) 2011-2015 Cyrus Daboo. All rights reserved.
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
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS


class Patch(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_PATCH_TARGET,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def getType(self):
        return definitions.cICalComponent_PATCH

    def duplicate(self, parent=None):
        return super(Component, self).duplicate(parent=parent)

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_PATCH_TARGET,
            definitions.cICalProperty_PATCH_DELETE,
            definitions.cICalProperty_PATCH_PARAMETER,
        )

Component.registerComponent(definitions.cICalComponent_PATCH, Patch)
