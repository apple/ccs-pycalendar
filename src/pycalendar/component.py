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

from componentbase import PyCalendarComponentBase
from datetime import PyCalendarDateTime
from property import PyCalendarProperty
import definitions
import stringutils

import os
import time
import uuid

class PyCalendarComponent(PyCalendarComponentBase):

    uid_ctr = 1

    def __init__(self, parent=None):
        
        super(PyCalendarComponent, self).__init__(parent)
        self.mUID = ""
        self.mSeq = 0
        self.mOriginalSeq = 0
        self.mChanged = False

    def duplicate(self, parent=None, **args):
        
        other = super(PyCalendarComponent, self).duplicate(parent=parent, **args)
        other.mUID = self.mUID
        other.mSeq = self.mSeq
        other.mOriginalSeq = self.mOriginalSeq

        other.mChanged = self.mChanged
        
        return other

    def __repr__(self):
        return "%s: UID: %s" % (self.getType(), self.getMapKey(),)
 
    def getMimeComponentName(self):
        raise NotImplementedError

    def getMapKey(self):
        if hasattr(self, "mMapKey"):
            return self.mMapKey
        elif self.mUID:
            return self.mUID
        else:
            self.mMapKey = str(uuid.uuid4())
            return self.mMapKey

    def getMasterKey(self):
        return self.mUID

    def getUID(self):
        return self.mUID

    def setUID(self, uid):
        if uid:
            self.mUID = uid
        else:
            # Get left-side of UID (first 24 chars of MD5 digest of time, pid
            # and ctr)
            lhs_txt = ""
            lhs_txt += str(time.time())
            lhs_txt += "."
            lhs_txt += str(os.getpid())
            lhs_txt += "."
            lhs_txt += str(PyCalendarComponent.uid_ctr)
            PyCalendarComponent.uid_ctr += 1
            lhs = stringutils.md5digest(lhs_txt)

            # Get right side (domain) of message-id
            rhs = None

            # Use app name
            from pycalendar.calendar import PyCalendar
            domain = PyCalendar.sDomain
            domain += str(PyCalendarComponent.uid_ctr)

            # Use first 24 chars of MD5 digest of the domain as the
            # right-side of message-id
            rhs = stringutils.md5digest(domain)

            # Generate the UID string
            new_uid = lhs
            new_uid += "@"
            new_uid += rhs

            self.mUID = new_uid

        self.removeProperties(definitions.cICalProperty_UID)

        prop = PyCalendarProperty(definitions.cICalProperty_UID, self.mUID)
        self.addProperty(prop)

    def getSeq(self):
        return self.mSeq

    def setSeq(self, seq):
        self.mSeq = seq

        self.removeProperties(definitions.cICalProperty_SEQUENCE)

        prop = PyCalendarProperty(definitions.cICalProperty_SEQUENCE, self.mSeq)
        self.addProperty(prop)

    def getOriginalSeq(self):
        return self.mOriginalSeq

    def getChanged(self):
        return self.mChanged

    def setChanged(self, changed):
        self.mChanged = changed

    def initDTSTAMP(self):
        self.removeProperties(definitions.cICalProperty_DTSTAMP)

        prop = PyCalendarProperty(definitions.cICalProperty_DTSTAMP,
                                  PyCalendarDateTime.getNowUTC())
        self.addProperty(prop)

    def updateLastModified(self):
        self.removeProperties(definitions.cICalProperty_LAST_MODIFIED)

        prop = PyCalendarProperty(definitions.cICalProperty_LAST_MODIFIED,
                                  PyCalendarDateTime.getNowUTC())
        self.addProperty(prop)

    def finalise(self):
        # Get UID
        temps = self.loadValueString(definitions.cICalProperty_UID)
        if temps is not None:
            self.mUID = temps

        # Get SEQ
        temp = self.loadValueInteger(definitions.cICalProperty_SEQUENCE)
        if temp is not None:
            self.mSeq = temp

        # Cache the original sequence when the component is read in.
        # This will be used to synchronise changes between two instances of the
        # same calendar
        self.mOriginalSeq = self.mSeq

    def canGenerateInstance(self):
        return True

    def getTimezones(self, tzids):
        # Look for all date-time properties
        for props in self.mProperties.itervalues():
            for prop in props:
                # Try to get a date-time value from the property
                dtv = prop.getDateTimeValue()
                if dtv is not None:
                    # Add timezone id if appropriate
                    if dtv.getValue().getTimezoneID():
                        tzids.add(dtv.getValue().getTimezoneID())
