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

from pycalendar.value import PyCalendarValue

class PyCalendarUTCOffsetValue( PyCalendarValue ):

    def __init__( self, value = 0 ):
        self.mValue = value

    def duplicate(self):
        return PyCalendarUTCOffsetValue(self.mValue)

    def getType( self ):
        return PyCalendarValue.VALUETYPE_UTC_OFFSET

    def parse( self, data ):
        # Must be of specific lengths
        datalen = len(data)
        if datalen not in (5, 7):
            self.mValue = 0
            raise ValueError

        # Get sign
        if data[0] not in ('+', '-'):
            raise ValueError
        plus = ( data[0] == '+' )

        # Get hours
        hours = int(data[1:3])

        # Get minutes
        mins = int(data[3:5])

        # Get seconds if present
        secs = 0
        if datalen == 7 :
            secs = int(data[5:])


        self.mValue = ((hours * 60) + mins) * 60 + secs
        if not plus:
            self.mValue = -self.mValue
 
    # os - StringIO object
    def generate( self, os ):
        try:
            abs_value = self.mValue
            if self.mValue < 0 :
                os.write( "-" )
                abs_value = -self.mValue
            else:
                os.write( "+" )

            secs = abs_value % 60
            mins = ( abs_value / 60 ) % 60
            hours = abs_value / ( 60 * 60 )

            if ( hours < 10 ):
                os.write( "0" )
            os.write( str( hours ) )
            if ( mins < 10 ):
                os.write( "0" )
            os.write( str( mins ) )
            if ( secs != 0 ):
                if ( secs < 10 ):
                    os.write( "0" )
                os.write( str( secs ) )
        except:
            pass

    def getValue( self ):
        return self.mValue

    def setValue( self, value ):
        self.mValue = value

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_UTC_OFFSET, PyCalendarUTCOffsetValue)

