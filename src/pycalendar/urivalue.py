##
#    Copyright (c) 2007-2013 Cyrus Daboo. All rights reserved.
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

from pycalendar import xmldefinitions, utils
from pycalendar.plaintextvalue import PlainTextValue
from pycalendar.value import Value
from pycalendar.parser import ParserContext

class URIValue(PlainTextValue):

    def getType(self):
        return URIValue.VALUETYPE_URI


    def parse(self, data, variant):

        if ParserContext.BACKSLASH_IN_URI_VALUE == ParserContext.PARSER_FIX:
            # Decoding required
            self.mValue = utils.decodeTextValue(data)
        else:
            # No decoding required
            self.mValue = data


    # os - StringIO object
    def generate(self, os):
        """
        Handle a client bug where it sometimes includes a \n in the value and we need
        to make sure that gets encoded rather than included literally which would break syntax.
        """
        if '\n' in self.mValue:
            try:
                # No encoding required
                os.write(self.mValue.replace("\n", "\\n"))
            except:
                pass
        else:
            super(URIValue, self).generate(os)

Value.registerType(Value.VALUETYPE_URI, URIValue, xmldefinitions.value_uri)
