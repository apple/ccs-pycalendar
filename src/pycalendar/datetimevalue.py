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

from pycalendar import xmldefs
from pycalendar.datetime import PyCalendarDateTime
from pycalendar.value import PyCalendarValue

class PyCalendarDateTimeValue(PyCalendarValue):

    def __init__(self, value=None):
        self.mValue = value if value is not None else PyCalendarDateTime()

    def duplicate(self):
        return PyCalendarDateTimeValue(self.mValue.duplicate())

    def getType(self):
        return  (PyCalendarValue.VALUETYPE_DATETIME, PyCalendarValue.VALUETYPE_DATE)[self.mValue.isDateOnly()]

    def parse(self, data, fullISO=False):
        self.mValue.parse(data, fullISO)

    def generate(self, os):
        self.mValue.generate(os)

    def writeXML(self, node, namespace):
        self.mValue.writeXML(node, namespace)

    def writeJSONValue(self, jobject):
        self.mValue.writeJSON(jobject)

    def getValue(self):
        return self.mValue

    def setValue(self, value):
        self.mValue = value

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_DATE, PyCalendarDateTimeValue, xmldefs.value_date)
PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_DATETIME, PyCalendarDateTimeValue, xmldefs.value_date_time)
