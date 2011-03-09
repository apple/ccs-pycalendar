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

"""
ICalendar attribute.

The attribute can consist of one or more values, all string.
"""

class PyCalendarAttribute(object):

    def __init__( self, name, value = None ):
        self.mName = name
        self.mValues = [value] if value is not None else []

    def duplicate(self):
        other = PyCalendarAttribute(self.mName, [i for i in self.mValues])
        other.mValues = [i for i in self.mValues]
        return other
        
    def getName( self ):
        return self.mName

    def setName( self, name ):
        self.mName = name

    def getFirstValue( self ):
        return self.mValues[0]

    def getValues( self ):
        return self.mValues

    def setValues( self, values ):
        self.mValues = values

    def addValue( self, value ):
        self.mValues.append( value )

    def generate( self, os ):
        try:
            os.write( self.mName )
            os.write( "=" )

            first = True
            for s in self.mValues:
                if first:
                    first = False
                else:
                    os.write( "," )

                # Write with quotation if required
                self.generateValue( os, s )

        except:
            # We ignore errors
            pass
    
    def generateValue( self, os, str ):
        # Look for quoting
        if str.find( ":" ) != -1 or str.find( ";" ) != -1 or str.find( "," ) != -1:
            os.write( "\"%s\"" % (str,) )
        else:
            os.write( str )
