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

# iCalendar UTC Offset value

from cStringIO import StringIO
from pycalendar import xmldefinitions
from pycalendar.value import Value

class UTCOffsetValue(Value):

    def __init__(self, value=0):
        self.mValue = value


    def duplicate(self):
        return UTCOffsetValue(self.mValue)


    def getType(self):
        return Value.VALUETYPE_UTC_OFFSET


    def parse(self, data, variant):

        fullISO = (variant == "vcard")

        # Must be of specific lengths
        datalen = len(data)
        if datalen not in ((6, 9,) if fullISO else (5, 7,)):
            self.mValue = 0
            raise ValueError

        # Get sign
        if data[0] not in ('+', '-'):
            raise ValueError
        plus = (data[0] == '+')

        # Get hours
        hours = int(data[1:3])

        # Get minutes
        index = 4 if fullISO else 3
        mins = int(data[index:index + 2])

        # Get seconds if present
        secs = 0
        if datalen > 6:
            index = 7 if fullISO else 5
            secs = int(data[index:])

        self.mValue = ((hours * 60) + mins) * 60 + secs
        if not plus:
            self.mValue = -self.mValue


    # os - StringIO object
    def generate(self, os, fullISO=False):
        try:
            abs_value = self.mValue
            if abs_value < 0 :
                sign = "-"
                abs_value = -self.mValue
            else:
                sign = "+"

            secs = abs_value % 60
            mins = (abs_value / 60) % 60
            hours = abs_value / (60 * 60)

            s = ("%s%02d:%02d" if fullISO else "%s%02d%02d") % (sign, hours, mins,)
            if (secs != 0):
                s = ("%s:%02d" if fullISO else "%s%02d") % (s, secs,)

            os.write(s)
        except:
            pass


    def writeXML(self, node, namespace):

        os = StringIO()
        self.generate(os)
        text = os.getvalue()
        text = text[:-2] + ":" + text[-2:]

        value = self.getXMLNode(node, namespace)
        value.text = text


    def parseJSONValue(self, jobject):
        self.parse(str(jobject), variant="vcard")


    def writeJSONValue(self, jobject):

        os = StringIO()
        self.generate(os, fullISO=True)
        text = os.getvalue()
        jobject.append(text)


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value

Value.registerType(Value.VALUETYPE_UTC_OFFSET, UTCOffsetValue, xmldefinitions.value_utc_offset)
