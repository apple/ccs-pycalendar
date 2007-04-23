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

# ICalendar Value class

class PyCalendarValue(object):

    VALUETYPE_BINARY = 0
    VALUETYPE_BOOLEAN = 1
    VALUETYPE_CALADDRESS = 2
    VALUETYPE_DATE = 3
    VALUETYPE_DATETIME = 4
    VALUETYPE_DURATION = 5
    VALUETYPE_FLOAT = 6
    VALUETYPE_GEO = 7
    VALUETYPE_INTEGER = 8
    VALUETYPE_PERIOD = 9
    VALUETYPE_RECUR = 10
    VALUETYPE_TEXT = 11
    VALUETYPE_TIME = 12
    VALUETYPE_URI = 13
    VALUETYPE_UTC_OFFSET = 14
    VALUETYPE_MULTIVALUE = 15
    VALUETYPE_XNAME = 16
    
    _typeMap = {}
    
    @classmethod
    def registerType(clz, type, cls):
        clz._typeMap[type] = cls
    
    @classmethod
    def createFromType(clz, type):
        # Create the type
        created = clz._typeMap.get(type, None)
        if created:
            return created()
        else:
            return clz._typeMap.get("DUMMY")(type)
    
    def copy(self):
        classType = PyCalendarValue._typeMap.get(self.getType(), None)
        return classType(copyit=self)

    def getType(self):
        raise NotImplemented

    def parse(self, data):
        raise NotImplemented
    
    def generate(self, os):
        raise NotImplemented
    