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

from componentbase import PyCalendarComponentBase
from datetime import PyCalendarDateTime
from property import PyCalendarProperty
import definitions
import stringutils
import time

class PyCalendarComponent(PyCalendarComponentBase):

    uid_ctr = 1;

    eVCALENDAR = -1;
    eVEVENT = 0;
    eVTODO = 1;
    eVJOURNAL = 2;
    eVFREEBUSY = 3;
    eVTIMEZONE = 4;
    eVALARM = 5;

    # Pseudo components
    eVTIMEZONESTANDARD = 6;
    eVTIMEZONEDAYLIGHT = 7;

    def __init__(self, calendar=None, copyit=None):
        
        if calendar:
            super(PyCalendarComponent, self).__init__()
            self.mCalendarRef = calendar
            self.mUID = ""
            self.mSeq = 0
            self.mOriginalSeq = 0
            self.mEmbedder = None
            self.mEmbedded = None
            self.mChanged = False
        elif copyit:
            super(PyCalendarComponent, self).__init__(copyit=copyit)
            self.mCalendarRef = copyit.mCalendarRef
            self.mUID = copyit.mUID
            self.mSeq = copyit.mSeq
            self.mOriginalSeq = copyit.mOriginalSeq
    
            self.mEmbedder = None
            self.mEmbedded = None
            if copyit.mEmbedded != None:
                # Do deep copy of element list
                self.mEmbedded = []
                for iter in copyit.mEmbedded:
                    self.mEmbedded.append(iter.clone_it())
                    self.mEmbedded[-1].setEmbedder(self)

            self.mETag = copyit.mETag
            self.mRURL = copyit.mRURL
            self.mChanged = copyit.mChanged

    def close(self):

        self.mEmbedder = None

        # Also close sub-components if present
        if (self.mEmbedded != None):
            for iter in self.mEmbedded:
                iter.close()
            self.mEmbedded.removeAllElements()
            self.mEmbedded = None

    def clone_it(self):
        raise NotImplemented

    def getType(self):
        raise NotImplemented

    def getBeginDelimiter(self):
        raise NotImplemented

    def getEndDelimiter(self):
        raise NotImplemented

    def getMimeComponentName(self):
        raise NotImplemented

    def addComponent(self, comp): #@UnusedVariable
        # Sub-classes decide what can be embedded
        return False

    def removeComponent(self, comp):
        if self.mEmbedded != None:
            try:
                self.mEmbedded.remove(comp)
            except ValueError:
                pass

    def hasEmbeddedComponent(self, type):
        if self.mEmbedded != None:
            for iter in self.mEmbedded:
                if iter.getType() == type:
                    return True
        return False

    def getFirstEmbeddedComponent(self, type):
        if self.mEmbedded != None:
            for iter in self.mEmbedded:
                if iter.getType() == type:
                    return iter
        return None

    def setEmbedder(self, embedder):
        self.mEmbedder = embedder

    def getEmbedder(self):
        return self.mEmbedder

    def setCalendar(self, ref):
        self.mCalendarRef = ref

    def getCalendar(self):
        return self.mCalendarRef

    def getMapKey(self):
        return self.mUID

    def getMasterKey(self):
        return self.mUID

    def getUID(self):
        return self.mUID

    def setUID(self, uid):
        if len(uid) != 0:
            self.mUID = uid
        else:
            # Get left-side of UID (first 24 chars of MD5 digest of time, clock
            # and ctr)
            lhs_txt = ""
            lhs_txt += str(time.time())
            lhs_txt += "."
            lhs_txt += str(PyCalendarComponent.uid_ctr)
            PyCalendarComponent.uid_ctr += 1
            lhs = stringutils.md5(lhs_txt)

            # Get right side (domain) of message-id
            rhs = None

            # Use app name
            domain = "com.mulberrymail"
            domain += PyCalendarComponent.uid_ctr

            # Use first 24 chars of MD5 digest of the domain as the
            # right-side of message-id
            rhs = stringutils.md5(domain)

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

    def getRURL(self):
        return self.mRURL

    def setRURL(self, rurl):
        self.mRURL = rurl

    def generateRURL(self):
        # Format is:
        #
        # <<hash code>> *("-0"> .ics
        if (self.mRURL is None) or (len(self.mRURL) == 0):
            # Generate hash code
            hash = ""
            hash += self.getMapKey()
            hash += ":"
            hash += str(self.getSeq())
            hash += ":"

            dt = self.loadValueDateTime(definitions.cICalProperty_DTSTAMP)
            if dt is not None:
                hash += dt.getText()

            self.mRURL = stringutils.md5(hash)
        else:
            # Strip off .ics
            if self.mRURL.endswith(".ics"):
                self.mRURL = self.mRURL[:-4]

        # Add trailer
        self.mRURL += "-0.ics"

    def getETag(self):
        return self.mETag

    def setETag(self, etag):
        self.mETag = etag

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

    def added(self):
        # Also add sub-components if present
        if self.mEmbedded != None:
            for iter in self.mEmbedded:
                iter.added()

        self.mChanged = True

    def removed(self):
        # Also remove sub-components if present
        if self.mEmbedded != None:
            for iter in self.mEmbedded:
                iter.removed()

        self.mChanged = True

    def duplicated(self):
        # Remove SEQ, UID, DTSTAMP
        # These will be re-created when it is added to the calendar
        self.removeProperties(definitions.cICalProperty_UID)
        self.removeProperties(definitions.cICalProperty_SEQUENCE)
        self.removeProperties(definitions.cICalProperty_DTSTAMP)

        # Remove the cached values as well
        self.mUID = ""
        self.mSeq = 0
        self.mOriginalSeq = 0

        # Also duplicate sub-components if present
        if self.mEmbedded != None:
            for iter in self.mEmbedded:
                iter.duplicated()

        # Reset CalDAV items
        self.mETag = None
        self.mRURL = None
        self.mChanged = True

    def changed(self):
        # Bump the sequence
        self.setSeq(self.getSeq() + 1)

        # Update last-modified
        self.updateLastModified();

        # Also change sub-components
        if self.mEmbedded != None:
            for iter in self.mEmbedded:
                iter.changed();

        self.mChanged = True

        # Mark calendar as dirty
        from calendar import PyCalendar
        cal = PyCalendar.getICalendar(self.getCalendar())
        if cal != None:
            cal.changedComponent(self)

    def finalise(self):
        # Get UID
        temps = self.loadValueString(definitions.cICalProperty_UID);
        if temps != None:
            self.mUID = temps

        # Get SEQ
        temp = self.loadValueInteger(definitions.cICalProperty_SEQUENCE);
        if temp != None:
            self.mSeq = temp

        # Cache the original sequence when the component is read in.
        # This will be used to synchronise changes between two instances of the
        # same calendar
        self.mOriginalSeq = self.mSeq

        # Get CalDAV info if present
        temps = self.loadPrivateValue(definitions.cICalProperty_X_PRIVATE_RURL);
        if temps != None:
            self.mRURL = temps
        temps = self.loadPrivateValue(definitions.cICalProperty_X_PRIVATE_ETAG)
        if temps != None:
            self.mETag = temps

    def canGenerateInstance(self):
        return True

    def generate(self, os, for_cache):
        # Header
        os.write(self.getBeginDelimiter())
        os.write("\n")

        # Write each property
        self.writeProperties(os)

        # Do private properties if caching
        if for_cache:
            if (self.mRURL is not None) and (len(self.mRURL) != 0):
                self.writePrivateProperty(os,
                        definitions.cICalProperty_X_PRIVATE_RURL,
                        self.mRURL)
            if (self.mETag is not None) and (len(self.mETag) != 0):
                self.writePrivateProperty(os,
                        definitions.cICalProperty_X_PRIVATE_ETAG,
                        self.mETag)

        # Write each embedded component
        if self.mEmbedded != None:
            for iter in self.mEmbedded:
                iter.generate(os, for_cache)

        # Footer
        os.write(self.getEndDelimiter())
        os.write("\n")

    def generateFiltered(self, os, filter):
            # Header
            os.write(self.getBeginDelimiter())
            os.write("\n")

            # Write each property
            self.writePropertiesFiltered(os, filter)

            # Write each embedded component
            if self.mEmbedded != None:
                # Shortcut for alll sub-components
                if filter.isAllSubComponents():
                    for iter in self.mEmbedded.elements():
                        iter.generate(os, False)
                elif filter.hasSubComponentFilters():
                    for iter in self.mEmbedded.elements():
                        subcomp = iter
                        subfilter = filter.getSubComponentFilter(self.getType())
                        if subfilter != None:
                            subcomp.generateFiltered(os, subfilter)

            # Footer
            os.write(self.getEndDelimiter())
            os.write("\n")

    def getTimezones(self, tzids):
        # Look for all date-time properties
        for props in self.mProperties.itervalues():
            for prop in props:
                # Try to get a date-time value from the property
                dtv = prop.getDateTimeValue()
                if dtv is not None:
                    # Add timezone id if appropriate
                    if dtv.getValue().getTimezoneID() is not None:
                        tzids.add(dtv.getValue().getTimezoneID())
