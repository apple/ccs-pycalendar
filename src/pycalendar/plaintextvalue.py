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

# iCalendar UTC Offset value

from value import PyCalendarValue

class PyCalendarPlainTextValue( PyCalendarValue ):

    def __init__(self):
        self.mValue = ''

    def parse( self, data ):
        # No decoding required
        self.mValue = data
        
    # os - StringIO object
    def generate( self, os ):
        try:
            # No encoding required
            os.write( self.mValue )
        except:
            pass

    def getValue(self):
        return self.mValue

    def setValue( self, value ):
        self.mValue = value
