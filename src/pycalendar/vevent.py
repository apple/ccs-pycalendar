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
from pycalendar.property import PyCalendarProperty

class PyCalendarVEvent(PyCalendarComponentRecur):

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
