##
#    Copyright (c) 2007 Cyrus Daboo. All rights reserved.
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

from component import PyCalendarComponent
from componentrecur import PyCalendarComponentRecur
from property import PyCalendarProperty
import definitions
import itipdefinitions

class PyCalendarVEvent(PyCalendarComponentRecur):

    sBeginDelimiter = definitions.cICalComponent_BEGINVEVENT

    sEndDelimiter = definitions.cICalComponent_ENDVEVENT

    @staticmethod
    def getVBegin():
        return PyCalendarVEvent.sBeginDelimiter

    @staticmethod
    def getVEnd():
        return PyCalendarVEvent.sEndDelimiter

    def __init__(self, calendar):
        super(PyCalendarVEvent, self).__init__(calendar=calendar)
        self.mStatus = definitions.eStatus_VEvent_None

    def duplicate(self, calendar):
        other = super(PyCalendarVEvent, self).duplicate(calendar)
        other.mStatus = self.mStatus
        return other

    def getType(self):
        return PyCalendarComponent.eVEVENT

    def getBeginDelimiter(self):
        return PyCalendarVEvent.sBeginDelimiter

    def getEndDelimiter(self):
        return PyCalendarVEvent.sEndDelimiter

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VEVENT

    def addComponent(self, comp):
        # We can embed the alarm components only
        if comp.getType() == PyCalendarComponent.eVALARM:
            if self.mEmbedded is None:
                self.mEmbedded = []
            self.mEmbedded.append(comp)
            comp.setEmbedder(self)
            return True
        else:
            return False

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
