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

from pycalendar import xmldefinitions
from pycalendar.datetime import DateTime
from pycalendar.value import Value
from pycalendar.valueutils import WrapperValue

class DateTimeValue(WrapperValue, Value):

    _wrappedClass = DateTime
    _wrappedType = None # Depends on actual value

    def getType(self):
        return  (Value.VALUETYPE_DATETIME, Value.VALUETYPE_DATE)[self.mValue.isDateOnly()]


    def parse(self, data, variant):
        self.mValue.parse(data, fullISO=(variant == "vcard"))


    def writeXML(self, node, namespace):
        self.mValue.writeXML(node, namespace)

Value.registerType(Value.VALUETYPE_DATE, DateTimeValue, xmldefinitions.value_date)
Value.registerType(Value.VALUETYPE_DATETIME, DateTimeValue, xmldefinitions.value_date_time)
