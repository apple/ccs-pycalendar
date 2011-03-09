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

# iCalendar UTC Offset value

from value import PyCalendarValue

class PyCalendarDummyValue( PyCalendarValue ):

    def __init__( self, type ):
        self.mType = type
        self.mValue = ''

    def duplicate(self):
        other = PyCalendarDummyValue(self.mType)
        other.mValue = self.mValue
        return other

    def getType( self ):
        return self.mType

    def parse( self, data ):
        self.mValue = data
        
    # os - StringIO object
    def generate( self, os ):
        try:
            os.write( self.mValue )
        except:
            pass

    def getValue( self ):
        return self.mValue

    def setValue( self, value ):
        self.mValue = value

PyCalendarValue.registerType("DUMMY", PyCalendarDummyValue)
