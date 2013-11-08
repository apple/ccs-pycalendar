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

from pycalendar.datetime import DateTime

class ComponentExpanded(object):

    @staticmethod
    def sort_by_dtstart_allday(e1, e2):

        if e1.mInstanceStart.isDateOnly() and e2.mInstanceStart.isDateOnly():
            return e1.mInstanceStart < e2.mInstanceStart
        elif e1.mInstanceStart.isDateOnly():
            return True
        elif e2.mInstanceStart.isDateOnly():
            return False
        elif e1.mInstanceStart == e2.mInstanceStart:
            if e1.mInstanceEnd == e2.mInstanceEnd:
                # Put ones created earlier in earlier columns in day view
                return e1.getOwner().getStamp() < e2.getOwner().getStamp()
            else:
                # Put ones that end later in earlier columns in day view
                return e1.mInstanceEnd > e2.mInstanceEnd
        else:
            return e1.mInstanceStart < e2.mInstanceStart


    @staticmethod
    def sort_by_dtstart(e1, e2):
        if e1.mInstanceStart == e2.mInstanceStart:
            if (e1.mInstanceStart.isDateOnly() and not e2.mInstanceStart.isDateOnly() or
                not e1.mInstanceStart.isDateOnly() and e2.mInstanceStart.isDateOnly()):
                return e1.mInstanceStart.isDateOnly()
            else:
                return False
        else:
            return e1.mInstanceStart < e2.mInstanceStart


    def __init__(self, owner, rid):

        self.mOwner = owner
        self.initFromOwner(rid)


    def duplicate(self):
        other = ComponentExpanded(self.mOwner, None)
        other.mInstanceStart = self.mInstanceStart.duplicate()
        other.mInstanceEnd = self.mInstanceEnd.duplicate()
        other.mRecurring = self.mRecurring
        return other


    def close(self):
        # Clean-up
        self.mOwner = None


    def getOwner(self):
        return self.mOwner


    def getMaster(self):
        return self.mOwner


    def getTrueMaster(self):
        return self.mOwner.getMaster()


    def getInstanceStart(self):
        return self.mInstanceStart


    def getInstanceEnd(self):
        return self.mInstanceEnd


    def recurring(self):
        return self.mRecurring


    def isNow(self):
        # Check instance start/end against current date-time
        now = DateTime.getNowUTC()
        return self.mInstanceStart <= now and self.mInstanceEnd > now


    def initFromOwner(self, rid):
        # There are four possibilities here:
        #
        # 1: this instance is the instance for the master component
        #
        # 2: this instance is an expanded instance derived directly from the
        # master component
        #
        # 3: This instance is the instance for a slave (overridden recurrence
        # instance)
        #
        # 4: This instance is the expanded instance for a slave with a RANGE
        # parameter
        #

        # rid is not set if the owner is the master (case 1)
        if rid is None:
            # Just get start/end from owner
            self.mInstanceStart = self.mOwner.getStart()
            self.mInstanceEnd = self.mOwner.getEnd()
            self.mRecurring = False

        # If the owner is not a recurrence instance then it is case 2
        elif not self.mOwner.isRecurrenceInstance():
            # Derive start/end from rid and duration of master

            # Start of the recurrence instance is the recurrence id
            self.mInstanceStart = rid

            # End is based on original events settings
            if self.mOwner.hasEnd():
                self.mInstanceEnd = self.mInstanceStart + (self.mOwner.getEnd() - self.mOwner.getStart())
            else:
                self.mInstanceEnd = self.mInstanceStart.duplicate()

            self.mRecurring = True

        # If the owner is a recurrence item and the passed in rid is the same
        # as the component rid we have case 3
        elif rid == self.mOwner.getRecurrenceID():
            # Derive start/end directly from the owner
            self.mInstanceStart = self.mOwner.getStart()
            self.mInstanceEnd = self.mOwner.getEnd()

            self.mRecurring = True

        # case 4 - the complicated one!
        else:
            # We need to use the rid as the starting point, but adjust it by
            # the offset between the slave's
            # rid and its start
            self.mInstanceStart = rid + (self.mOwner.getStart() - self.mOwner.getRecurrenceID())

            # End is based on duration of owner
            self.mInstanceEnd = self.mInstanceStart + (self.mOwner.getEnd() - self.mOwner.getStart())

            self.mRecurring = True
