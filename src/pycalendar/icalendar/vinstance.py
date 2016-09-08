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


class VInstance(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_RECURRENCE_ID,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):

        super(Component, self).__init__(parent)
        self.mRecurrenceID = None

    def duplicate(self, parent=None, **args):

        other = super(Component, self).duplicate(parent=parent, **args)
        other.mRecurrenceID = self.mRecurrenceID.duplicate()
        return other

    def getType(self):
        return definitions.cICalComponent_VINSTANCE

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VINSTANCE

    def finalise(self):

        # Get RECURRENCE-ID
        self.mRecurrenceID = self.loadValueDateTime(definitions.cICalProperty_RECURRENCE_ID)

        # Update the map key
        self.mMapKey = self.mRecurrenceID.getText()

    def getRecurrenceID(self):
        return self.mRecurrenceID

    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_RECURRENCE_ID,
        )

Component.registerComponent(definitions.cICalComponent_VINSTANCE, VInstance)
