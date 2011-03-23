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

    (
        VALUETYPE_ADR,
        VALUETYPE_BINARY,
        VALUETYPE_BOOLEAN,
        VALUETYPE_CALADDRESS,
        VALUETYPE_DATE,
        VALUETYPE_DATETIME,
        VALUETYPE_DURATION,
        VALUETYPE_FLOAT,
        VALUETYPE_GEO,
        VALUETYPE_INTEGER,
        VALUETYPE_N,
        VALUETYPE_ORG,
        VALUETYPE_PERIOD,
        VALUETYPE_RECUR,
        VALUETYPE_REQUEST_STATUS,
        VALUETYPE_TEXT,
        VALUETYPE_TIME,
        VALUETYPE_URI,
        VALUETYPE_UTC_OFFSET,
        VALUETYPE_VCARD,
        VALUETYPE_MULTIVALUE,
        VALUETYPE_XNAME,
    ) = range(22)
    
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
