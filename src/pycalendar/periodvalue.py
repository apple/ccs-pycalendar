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

from period import PyCalendarPeriod
from value import PyCalendarValue

class PyCalendarPeriodValue( PyCalendarValue ):

    def __init__( self, value = None, copyit = None ):
        if value:
            self.mValue = value
        elif copyit:
            self.mValue = PyCalendarPeriod( copyit=copyit.mValue )
        else:
            self.mValue = PyCalendarPeriod()

    def getType( self ):
        return PyCalendarValue.VALUETYPE_PERIOD

    def parse( self, data ):
        self.mValue.parse( data )

    def generate( self, os ):
        self.mValue.generate( os )

    def getValue( self ):
        return self.mValue

    def setValue( self, value ):
        self.mValue = value

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_PERIOD, PyCalendarPeriodValue)
