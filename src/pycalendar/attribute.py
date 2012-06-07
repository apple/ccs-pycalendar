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

"""
ICalendar attribute.

The attribute can consist of one or more values, all string.
"""
import xml.etree.cElementTree as XML
from pycalendar import xmldefs

class PyCalendarAttribute(object):

    def __init__(self, name, value = None):
        self.mName = name
        if value is None:
            self.mValues = []
        elif isinstance(value, basestring):
            self.mValues = [value]
        else:
            self.mValues = value

    def duplicate(self):
        other = PyCalendarAttribute(self.mName)
        other.mValues = self.mValues[:]
        return other

    def __hash__(self):
        return hash((self.mName.upper(), tuple(self.mValues)))

    def __ne__(self, other): return not self.__eq__(other)
    def __eq__(self, other):
        if not isinstance(other, PyCalendarAttribute): return False
        return self.mName.upper() == other.mName.upper() and self.mValues == other.mValues

    def getName(self):
        return self.mName

    def setName(self, name):
        self.mName = name

    def getFirstValue(self):
        return self.mValues[0]

    def getValues(self):
        return self.mValues

    def setValues(self, values):
        self.mValues = values

    def addValue(self, value):
        self.mValues.append(value)

    def removeValue(self, value):
        self.mValues.remove(value)
        return len(self.mValues)

    def generate(self, os):
        try:
            os.write(self.mName)
            
            # To support vCard 2.1 syntax we allow parameters without values
            if self.mValues:
                os.write("=")
    
                first = True
                for s in self.mValues:
                    if first:
                        first = False
                    else:
                        os.write(",")
    
                    # Write with quotation if required
                    self.generateValue(os, s)

        except:
            # We ignore errors
            pass
    
    def generateValue(self, os, str):
        # Look for quoting
        if str.find(":") != -1 or str.find(";") != -1 or str.find(",") != -1:
            os.write("\"%s\"" % (str,))
        else:
            os.write(str)

    def writeXML(self, node, namespace):
        param = XML.SubElement(node, xmldefs.makeTag(namespace, self.getName()))
        for value in self.getValues():
            # TODO: need to figure out proper value types
            text = XML.SubElement(param, xmldefs.makeTag(namespace, xmldefs.value_text))
            text.text = value
