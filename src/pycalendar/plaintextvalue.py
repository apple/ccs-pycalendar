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

# iCalendar generic text-like value

from pycalendar.value import Value

class PlainTextValue(Value):

    def __init__(self, value=''):
        self.mValue = value


    def duplicate(self):
        return self.__class__(self.mValue)


    def parse(self, data, variant):
        # No decoding required
        self.mValue = data


    # os - StringIO object
    def generate(self, os):
        try:
            # No encoding required
            os.write(self.mValue)
        except:
            pass


    def writeXML(self, node, namespace):
        value = self.getXMLNode(node, namespace)
        value.text = self.mValue


    def parseJSONValue(self, jobject):
        self.mValue = str(jobject)


    def writeJSONValue(self, jobject):
        jobject.append(self.mValue)


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value
