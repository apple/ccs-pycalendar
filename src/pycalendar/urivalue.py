##
#    Copyright (c) 2007-2012 Cyrus Daboo. All rights reserved.
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

# iCalendar URI value

from pycalendar import xmldefs, utils
from pycalendar.plaintextvalue import PyCalendarPlainTextValue
from pycalendar.value import PyCalendarValue
from pycalendar.parser import ParserContext

class PyCalendarURIValue( PyCalendarPlainTextValue ):

    def getType(self):
        return PyCalendarURIValue.VALUETYPE_URI

    def parse( self, data ):
        
        if ParserContext.BACKSLASH_IN_URI_VALUE == ParserContext.PARSER_FIX:
            # Decoding required
            self.mValue = utils.decodeTextValue( data )
        else:
            # No decoding required
            self.mValue = data

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_URI, PyCalendarURIValue, xmldefs.value_uri)

        