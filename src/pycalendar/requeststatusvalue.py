##
#    Copyright (c) 2011-2012 Cyrus Daboo. All rights reserved.
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

# iCalendar REQUEST-STATUS value

from pycalendar import utils, xmldefs
from pycalendar.parser import ParserContext
from pycalendar.value import PyCalendarValue
import xml.etree.cElementTree as XML

class PyCalendarRequestStatusValue(PyCalendarValue):
    """
    The value is a list of strings (either 2 or 3 items)
    """

    def __init__(self, value=None):
        self.mValue = value if value is not None else ["2.0", "Success"]


    def __hash__(self):
        return hash(tuple(self.mValue))


    def duplicate(self):
        return PyCalendarRequestStatusValue(self.mValue[:])


    def getType(self):
        return PyCalendarValue.VALUETYPE_REQUEST_STATUS


    def parse(self, data):

        # Split fields based on ;
        code, rest = data.split(";", 1)

        if "\\" in code and ParserContext.INVALID_REQUEST_STATUS_VALUE in (ParserContext.PARSER_IGNORE, ParserContext.PARSER_FIX):
            code = code.replace("\\", "")
        elif ParserContext.INVALID_REQUEST_STATUS_VALUE == ParserContext.PARSER_RAISE:
            raise ValueError

        # The next two items are text with possible \; sequences so we have to punt on those
        desc = ""
        semicolon = rest.find(";")
        while semicolon != -1:
            if rest[semicolon - 1] == "\\":
                desc += rest[:semicolon + 1]
                rest = rest[semicolon + 1:]
                semicolon = rest.find(";")
            else:
                desc += rest[:semicolon]
                rest = rest[semicolon + 1:]
                break

        if semicolon == -1:
            desc += rest
            rest = ""

        # Decoding required
        self.mValue = [code, utils.decodeTextValue(desc), utils.decodeTextValue(rest) if rest else None]


    # os - StringIO object
    def generate(self, os):
        try:
            # Encoding required
            utils.writeTextValue(os, self.mValue[0])
            os.write(";")
            utils.writeTextValue(os, self.mValue[1])
            if len(self.mValue) == 3 and self.mValue[2]:
                os.write(";")
                utils.writeTextValue(os, self.mValue[2])
        except:
            pass


    def writeXML(self, node, namespace):
        code = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.req_status_code))
        code.text = self.mValue[0]

        description = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.req_status_description))
        description.text = self.mValue[1]

        if len(self.mValue) == 3 and self.mValue[2]:
            data = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.req_status_data))
            data.text = self.mValue[1]


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value

PyCalendarValue.registerType(PyCalendarValue.VALUETYPE_REQUEST_STATUS, PyCalendarRequestStatusValue, None)
