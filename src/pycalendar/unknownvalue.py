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

# iCalendar Unknown value - one whose default type we don't know about

from pycalendar import xmldefinitions
from pycalendar.plaintextvalue import PlainTextValue
from pycalendar.value import Value

class UnknownValue(PlainTextValue):

    def getType(self):
        return UnknownValue.VALUETYPE_UNKNOWN

Value.registerType(Value.VALUETYPE_UNKNOWN, UnknownValue, xmldefinitions.value_unknown)
