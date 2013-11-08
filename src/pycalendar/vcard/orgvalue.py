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

# vCard ORG value

from pycalendar import utils
from pycalendar.value import Value

class OrgValue(Value):
    """
    mValue is a str or tuple of str
    """

    def __init__(self, value=None):
        self.mValue = value


    def duplicate(self):
        return OrgValue(self.mValue)


    def getType(self):
        return Value.VALUETYPE_ORG


    def parse(self, data, variant="vcard"):
        self.mValue = utils.parseTextList(data, ';')


    def generate(self, os):
        utils.generateTextList(os, self.mValue, ';')


    def parseJSONValue(self, jobject):
        self.mValue = tuple(jobject)


    def writeJSONValue(self, jobject):
        jobject.append(list(self.mValue))


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value

Value.registerType(Value.VALUETYPE_ORG, OrgValue, None)
