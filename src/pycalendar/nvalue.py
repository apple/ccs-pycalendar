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

# vCard ADR value

from value import PyCalendarValue
from n import N

class NValue( PyCalendarValue ):

    def __init__(self, value = None):
        self.mValue = value if value is not None else N()

    def duplicate(self):
        return NValue(self.mValue.duplicate())

    def getType(self):
        return PyCalendarValue.VALUETYPE_N

    def parse(self, data):
        self.mValue.parse(data)

    def generate(self, os):
        self.mValue.generate(os)

    def getValue(self):
        return self.mValue

    def setValue(self, value):
        self.mValue = value

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_N, NValue)
