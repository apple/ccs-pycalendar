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

from pycalendar.value import PyCalendarValue

class PyCalendarMultiValue(PyCalendarValue):

    def __init__(self, type):

        self.mType = type
        self.mValues = []


    def __hash__(self):
        return hash(tuple(self.mValues))


    def duplicate(self):
        other = PyCalendarMultiValue(self.mType)
        other.mValues = [i.duplicate() for i in self.mValues]
        return other


    def getType(self):
        return self.mType


    def getRealType(self):
        return PyCalendarValue.VALUETYPE_MULTIVALUE


    def getValue(self):
        return self.mValues


    def getValues(self):
        return self.mValues


    def addValue(self, value):
        self.mValues.append(value)


    def setValue(self, value):
        newValues = []
        for v in value:
            pyCalendarValue = PyCalendarValue.createFromType(self.mType)
            pyCalendarValue.setValue(v)
            newValues.append(pyCalendarValue)
        self.mValues = newValues


    def parse(self, data):
        # Tokenize on comma
        if "," in data:
            tokens = data.split(",")
        else:
            tokens = (data,)
        for token in tokens:
            # Create single value, and parse data
            value = PyCalendarValue.createFromType(self.mType)
            value.parse(token)
            self.mValues.append(value)


    def generate(self, os):
        try:
            first = True
            for iter in self.mValues:
                if first:
                    first = False
                else:
                    os.write(",")
                iter.generate(os)
        except:
            pass


    def writeXML(self, node, namespace):
        for iter in self.mValues:
            iter.writeXML(node, namespace)


    def writeJSONValue(self, jobject):
        for iter in self.mValues:
            iter.writeJSONValue(jobject)

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_MULTIVALUE, PyCalendarMultiValue, None)
