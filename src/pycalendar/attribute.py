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
We optimise for the usual case of a single value by having a single string
attribute in the class, and then an array for multi-values, which is None
unless there is more than one value.
"""

class PyCalendarAttribute(object):

    def __init__( self, name = None, value = None, copyit = None ):
        
        if name and value:
            self.mName = name
            self.mValue = value
            self.mValues = None
        elif copyit:
            self.mName = copyit.mName
            self.mValue = copyit.mValue
            if copyit.mValues is not None:
                self.mValues = [i for i in copyit.mValues]
            else:
                self.mValues = None
        else:
            self.mName = ''
            self.mValue = ''
            self.mValues = None

    def getName( self ):
        return self.mName

    def setName( self, name ):
        self.mName = name

    def getFirstValue( self ):
        if self.mValues is not None:
            return self.mValues[0]
        else:
            return self.mValue

    def getValues( self ):
        return self.mValues

    def setValues( self, values ):
        self.mValues = values

    def addValue( self, value ):
        # See if switch from single to multi-value is needed
        if self.mValues is None:
            self.mValues = []
            self.mValues.append( self.mValue )
            self.mValue = None
        self.mValues.append( value )

    def generate( self, os ):
        try:
            os.write( self.mName )
            os.write( "=" )

            if self.mValues is None:
                # Write with quotation if required
                self.generateValue( os, self.mValue )
            else:
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
