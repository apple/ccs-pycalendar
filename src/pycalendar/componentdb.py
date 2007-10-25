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

from componentrecur import PyCalendarComponentRecur
from datetime import PyCalendarDateTime

class PyCalendarComponentDB(object):

    def __init__(self, copyit=None):
        self.mItems = {}
        if copyit:
            self.mRecurMap = None
            if (copyit.mRecurMap != None):
                self.mRecurMap = {}
                for key, value in copyit.mRecurMap.items():
                    list = []
                    for item in value:
                        list.append(PyCalendarDateTime(copyit=item))
                    self.mRecurMap[key] = list
        else:
            self.mRecurMap = None

    def __iter__(self):
        return self.mItems.itervalues()

    def __getitem__(self, i):
        return self.mItems[i]

    def has_key(self, k):
        return self.mItems.has_key(k)

    def close(self):
        for value in self.mItems.values():
            # Tell component it is removed and delete it
            value.close()

        self.mItems.clear()

    def addComponent(self, comp):
        # Must have valid UID
        if (len(comp.getMapKey()) == 0):
            return False

        # Add the component to the calendar
        bresult = True

        # See if duplicate
        if self.mItems.has_key(comp.getMapKey()):
            result = self.mItems.get(comp.getMapKey())

            # Replace existing if sequence is higher
            if comp.getSeq() > result.getSeq():
                self.mItems[comp.getMapKey()] = comp
                bresult = True
            else:
                bresult = False
        else:
            self.mItems[comp.getMapKey()] = comp
            bresult = True

        # Now look for a recurrence component if it was added
        if bresult and isinstance(comp, PyCalendarComponentRecur):

            recur = comp

            # Add each overridden instance to the override map
            if recur.isRecurrenceInstance():
                # Look for existiung UID->RID map entry
                if self.mRecurMap == None:
                    self.mRecurMap = {}
                found = self.mRecurMap.get(recur.getUID(), None)
                if found != None:
                    # Add to existing list
                    found.append(recur.getRecurrenceID())
                else:
                    # Create new entry for this UID
                    temp = []
                    temp.append(recur.getRecurrenceID())
                    self.mRecurMap[recur.getUID()] = temp

                # Now try and find the master component if it currently exists
                found2 = self.mItems.get(recur.getUID(), None)
                if found2 != None:
                    # Tell the instance who its master is
                    recur.setMaster(found2)

            # Make sure the master is sync'd with any instances that may have
            # been
            # added before it, those added after
            # will be sync'd when they are added
            elif self.mRecurMap != None:
                # See if master has an entry in the UID->RID map
                found = self.mRecurMap.get(comp.getUID(), None)
                if found != None:
                    # Make sure each instance knows about its master
                    for iter in found:
                        # Get the instance
                        instance = self.getRecurrenceInstance(comp.getUID(), iter)
                        if instance != None:
                            # Tell the instance who its master is
                            instance.setMaster(recur)

        # Tell component it has now been added
        if bresult:
            comp.added()

        return bresult

    def removeComponent(self, comp):
        # Tell component it is removed
        comp.removed()

        # Only if present
        if self.mItems.has_key(comp.getMapKey()):
            del self.mItems[comp.getMapKey()]

    def removeAllComponents(self):
        for comp in self.mItems.values():
            # Tell component it is removed and delete it
            comp.removed()
            comp.close()

        self.clear()

    def changedComponent(self, comp):
        # Tell component it is changed
        comp.changed()

    def getRecurrenceInstancesIds(self, uid, ids):
        if self.mRecurMap == None:
            return []

        # Look for matching UID in recurrence instance map
        found = self.mRecurMap.get(uid, None)
        if found != None:
            # Return the recurrence ids
            return found

        return []

    def getRecurrenceInstanceItems(self, uid, items):
        if self.mRecurMap == None:
            return

        # Look for matching UID in recurrence instance map
        found = self.mRecurMap.get(uid, None)
        if found != None:
            # Return all the recurrence ids
            for iter in found:
                # Look it up
                recur = self.getRecurrenceInstance(uid, iter)
                if recur != None:
                    items.append(recur)

    def getRecurrenceInstance(self, uid, rid):
        found = self.mItems.get(PyCalendarComponentRecur.mapKey(uid, rid.getText()), None)
        if found != None:
            # Tell the instance who its master is
            return found

        return None
