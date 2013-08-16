##
#    Copyright (c) 2007-2012 Cyrus Daboo. All rights reserved.
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

from pycalendar import stringutils
from pycalendar.componentbase import ComponentBase
from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions
from pycalendar.icalendar.property import Property
import os
import time
import uuid

class Component(ComponentBase):

    uid_ctr = 1

    mapper = {}

    sComponentType = None
    sPropertyType = Property

    @classmethod
    def registerComponent(cls, name, comptype):
        cls.mapper[name] = comptype


    @classmethod
    def makeComponent(cls, compname, parent):
        try:
            return cls.mapper[compname](parent=parent)
        except KeyError:
            return cls.mapper[definitions.cICalComponent_UNKNOWN](parent=parent, comptype=compname)


    def __init__(self, parent=None):

        super(Component, self).__init__(parent)
        self.mUID = ""
        self.mSeq = 0
        self.mOriginalSeq = 0
        self.mChanged = False


    def duplicate(self, parent=None, **args):

        other = super(Component, self).duplicate(parent=parent, **args)
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


    def getSortKey(self):
        return self.getMapKey()


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
            lhs_txt += str(Component.uid_ctr)
            Component.uid_ctr += 1
            lhs = stringutils.md5digest(lhs_txt)

            # Get right side (domain) of message-id
            rhs = None

            # Use app name
            from pycalendar.icalendar.calendar import Calendar
            domain = Calendar.sDomain
            domain += str(Component.uid_ctr)

            # Use first 24 chars of MD5 digest of the domain as the
            # right-side of message-id
            rhs = stringutils.md5digest(domain)

            # Generate the UID string
            new_uid = lhs
            new_uid += "@"
            new_uid += rhs

            self.mUID = new_uid

        self.removeProperties(definitions.cICalProperty_UID)

        prop = Property(definitions.cICalProperty_UID, self.mUID)
        self.addProperty(prop)


    def getSeq(self):
        return self.mSeq


    def setSeq(self, seq):
        self.mSeq = seq

        self.removeProperties(definitions.cICalProperty_SEQUENCE)

        prop = Property(definitions.cICalProperty_SEQUENCE, self.mSeq)
        self.addProperty(prop)


    def getOriginalSeq(self):
        return self.mOriginalSeq


    def getChanged(self):
        return self.mChanged


    def setChanged(self, changed):
        self.mChanged = changed


    def initDTSTAMP(self):
        self.removeProperties(definitions.cICalProperty_DTSTAMP)

        prop = Property(definitions.cICalProperty_DTSTAMP,
                                  DateTime.getNowUTC())
        self.addProperty(prop)


    def updateLastModified(self):
        self.removeProperties(definitions.cICalProperty_LAST_MODIFIED)

        prop = Property(definitions.cICalProperty_LAST_MODIFIED,
                                  DateTime.getNowUTC())
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

Component.sComponentType = Component
