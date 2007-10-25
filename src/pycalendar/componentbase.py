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

from datetimevalue import PyCalendarDateTimeValue
from periodvalue import PyCalendarPeriodValue
from property import PyCalendarProperty
from value import PyCalendarValue

class PyCalendarComponentBase(object):

    def __init__(self, copyit=None):
        if copyit:
            self.mProperties = {}
            for prop in copyit.mProperties:
                self.mProperties.setdefault(prop.getName(), []).append(PyCalendarProperty(copyit=prop))
        else:
            self.mProperties = {}

    def getProperties(self):
        return self.mProperties

    def setProperties(self, props):
        self.mProperties = props

    def addProperty(self, prop):
        self.mProperties.setdefault(prop.getName(), []).append(prop)

    def hasProperty(self, prop):
        return self.mProperties.has_key(prop)

    def countProperty(self, prop):
        return len(self.mProperties.get(prop, []))

    def findFirstProperty(self, prop):
        return self.mProperties.get(prop, [None])[0]

    def removeProperties(self, prop):
        if self.mProperties.has_key(prop):
            del self.mProperties[prop]

    def getPropertyInteger(self, prop, type = None):
        return self.loadValueInteger(prop, type)

    def getPropertyString(self, prop):
        return self.loadValueString(prop)

    def getProperty(self, prop, value):
        return self.loadValue(prop, value)

    def finalise(self):
        raise NotImplemented

    def generate(self, os, for_cache):
        raise NotImplemented

    def generateFiltered(self, os, filter):
        raise NotImplemented

    def loadValue(self, value_name):
        if self.getProperties().has_key(value_name):
            return self.getProperties()[value_name][0]

        return None

    def loadValueInteger(self, value_name, type=None):
        if type:
            if self.getProperties().has_key(value_name):
                if type == PyCalendarValue.VALUETYPE_INTEGER:
                    ivalue = self.getProperties()[value_name][0].getIntegerValue()
                    if ivalue != None:
                        return ivalue.getValue()
                elif type == PyCalendarValue.VALUETYPE_UTC_OFFSET:
                    uvalue = self.getProperties()[value_name][0].getUTCOffsetValue()
                    if (uvalue != None):
                        return uvalue.getValue()
    
            return None
        else:
            return self.loadValueInteger(value_name, PyCalendarValue.VALUETYPE_INTEGER)

    def loadValueString(self, value_name):
        if self.getProperties().has_key(value_name):
            tvalue = self.getProperties()[value_name][0].getTextValue()
            if (tvalue != None):
                return tvalue.getValue()

        return None

    def loadValueDateTime(self, value_name):
        if self.getProperties().has_key(value_name):
            dtvalue = self.getProperties()[value_name][0].getDateTimeValue()
            if dtvalue != None:
                return dtvalue.getValue()

        return None

    def loadValueDuration(self, value_name):
        if self.getProperties().has_key(value_name):
            dvalue = self.getProperties()[value_name][0].getDurationValue()
            if (dvalue != None):
                return dvalue.getValue()

        return None

    def loadValuePeriod(self, value_name):
        if self.getProperties().has_key(value_name):
            pvalue = self.getProperties()[value_name][0].getPeriodValue()
            if (pvalue != None):
                return pvalue.getValue()

        return None

    def loadValueRRULE(self, value_name, value, add):
        # Get RRULEs
        if self.getProperties().has_key(value_name):
            items = self.getProperties()[value_name]
            for iter in items:
                rvalue = iter.getRecurrenceValue()
                if (rvalue != None):
                    if add:
                        value.addRule(rvalue.getValue())
                    else:
                        value.subtractRule(rvalue.getValue())
            return True
        else:
            return False

    def loadValueRDATE(self, value_name, value, add):
        # Get RDATEs
        if self.getProperties().has_key(value_name):
            items = self.getProperties()[value_name]
            for iter in items:
                mvalue = iter.getMultiValue()
                if (mvalue != None):
                    for obj in mvalue.getValues():
                        # cast to date-time
                        if isinstance(obj, PyCalendarDateTimeValue):
                            if add:
                                value.addDT(obj.getValue())
                            else:
                                value.subtractDT(obj.getValue())
                        elif isinstance(obj, PyCalendarPeriodValue):
                            if add:
                                value.addDT(obj.getValue().getStart())
                            else:
                                value.subtractDT(obj.getValue().getStart())

            return True
        else:
            return False

    def writeProperties(self, os):
        for props in self.mProperties.itervalues():
            for prop in props:
                prop.generate(os)

    def writePropertiesFiltered(self, os, filter):

        # Shortcut for all properties
        if filter.isAllProperties():
            for props in self.mProperties.itervalues():
                for prop in props:
                    prop.generate(os)
        elif filter.hasPropertyFilters():
            for props in self.mProperties.itervalues():
                for prop in props:
                    prop.generateFiltered(os, filter)

    def loadPrivateValue(self, value_name):
        # Read it in from properties list and then delete the property from the
        # main list
        result = self.loadValueString(value_name)
        if (result != None):
            self.removeProperties(value_name)
        return result

    def writePrivateProperty(self, os, key, value):
        prop = PyCalendarProperty(name=key, value=value)
        prop.generate(os)

    def editProperty(self, propname, propvalue):

        # Remove existing items
        self.removeProperties(propname)

        # Now create properties
        if (propvalue != None) and (len(propvalue) != 0):
            self.addProperty(PyCalendarProperty(name=propname, value=propvalue))
