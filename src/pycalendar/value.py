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

# ICalendar Value class

from cStringIO import StringIO

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
    VALUETYPE_REQUEST_STATUS = 11
    VALUETYPE_TEXT = 12
    VALUETYPE_TIME = 13
    VALUETYPE_URI = 14
    VALUETYPE_UTC_OFFSET = 15
    VALUETYPE_MULTIVALUE = 16
    VALUETYPE_XNAME = 17
    
    _typeMap = {}
    
    def __str__(self):
        return self.getText()

    def __hash__(self):
        return hash((self.getType(), self.getValue()))

    def __ne__(self, other): return not self.__eq__(other)
    def __eq__(self, other):
        if not isinstance(other, PyCalendarValue): return False
        return self.getType() == other.getType() and self.getValue() == other.getValue()

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
    
    def getType(self):
        raise NotImplementedError

    def getRealType(self):
        return self.getType()

    def parse(self, data):
        raise NotImplementedError
    
    def generate(self, os):
        raise NotImplementedError
    
    def getText(self):
        os = StringIO()
        self.generate(os)
        return os.getvalue()

    def getValue( self ):
        raise NotImplementedError

    def setValue( self, value ):
        raise NotImplementedError
