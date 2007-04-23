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

from value import PyCalendarValue

class PyCalendarMultiValue( PyCalendarValue ):

    def __init__( self, type = None, copyit = None ):

        if type:
            self.mType = type
            self.mValues = []
        elif copyit:
            self.mType = copyit.mType
            self.mValues = [i.copy() for i in copyit.mValues]

    def getType( self ):
        return self.mType

    def getValues( self ):
        return self.mValues

    def addValue( self, value ):
        self.mValues.append( value )

    def parse( self, data ):
        # Tokenize on comma
        tokens = data.split( "," )
        for token in tokens:
            # Create single value, and parse data
            value = PyCalendarValue.createFromType( self.mType )
            value.parse( token )
            self.mValues.append( value )

    def generate( self, os ):
        try:
            first = True
            for iter in self.mValues:
                if first:
                    first = False
                else:
                    os.write( "," )
                iter.generate( os )
        except:
            pass
            