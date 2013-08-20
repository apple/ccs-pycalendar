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


class OutputFilter(object):

    def __init__(self, type):
        self.mType = type
        self.mAllSubComponents = False
        self.mSubComponents = None
        self.mAllProperties = False
        self.mProperties = None


    def getType(self):
        return self.mType


    # Test to see if component type can be written out
    def testComponent(self, oftype):
        return self.mType == oftype


    def isAllSubComponents(self):
        return self.mAllSubComponents


    def setAllSubComponents(self):
        self.mAllSubComponents = True
        self.mSubComponents = None


    def addSubComponent(self, comp):
        if self.mSubComponents == None:
            self.mSubComponents = {}

        self.mSubComponents[comp.getType()] = comp


    # Test to see if sub-component type can be written out
    def testSubComponent(self, oftype):
        return self.mAllSubComponents or (self.mSubComponents is not None) \
                and oftype in self.mSubComponents


    def hasSubComponentFilters(self):
        return self.mSubComponents is not None


    def getSubComponentFilter(self, type):
        if self.mSubComponents is not None:
            return self.mSubComponents.get(type, None)
        else:
            return None


    def isAllProperties(self):
        return self.mAllProperties


    def setAllProperties(self):
        self.mAllProperties = True
        self.mProperties = None


    def addProperty(self, name, no_value):
        if self.mProperties is None:
            self.mProperties = {}

        self.mProperties[name] = no_value


    def hasPropertyFilters(self):
        return self.mProperties is not None


    # Test to see if property can be written out and also return whether
    # the property value is used
    def testPropertyValue(self, name):

        if self.mAllProperties:
            return True, False

        if self.mProperties is None:
            return False, False

        result = self.mProperties.get(name, None)
        return result is not None, result
