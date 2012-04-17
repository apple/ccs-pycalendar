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

from pycalendar import xmldefs
from pycalendar.recurrence import PyCalendarRecurrence
from pycalendar.value import PyCalendarValue

class PyCalendarRecurrenceValue( PyCalendarValue ):

    def __init__( self, value = None ):
        self.mValue = value if value is not None else PyCalendarRecurrence()

    def duplicate(self):
        return PyCalendarRecurrenceValue(self.mValue.duplicate())

    def getType( self ):
        return PyCalendarValue.VALUETYPE_RECUR

    def parse( self, data ):
        self.mValue.parse( data )

    def generate( self, os ):
        self.mValue.generate( os )

    def writeXML(self, node, namespace):
        self.mValue.writeXML(node, namespace)

    def writeJSON(self, jobject):
        self.mValue.writeJSON(jobject)

    def getValue( self ):
        return self.mValue

    def setValue( self, value ):
        self.mValue = value

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_RECUR, PyCalendarRecurrenceValue, xmldefs.value_recur)
