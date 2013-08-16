##
#    Copyright (c) 2011-2013 Cyrus Daboo. All rights reserved.
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

from pycalendar import utils, xmlutils
from pycalendar.icalendar import xmldefinitions
from pycalendar.parser import ParserContext
from pycalendar.value import Value
import xml.etree.cElementTree as XML

class RequestStatusValue(Value):
    """
    The value is a list of strings (either 2 or 3 items)
    """

    def __init__(self, value=None):
        self.mValue = value if value is not None else ["2.0", "Success"]


    def __hash__(self):
        return hash(tuple(self.mValue))


    def duplicate(self):
        return RequestStatusValue(self.mValue[:])


    def getType(self):
        return Value.VALUETYPE_REQUEST_STATUS


    def parse(self, data, variant="icalendar"):

        result = utils.parseTextList(data, always_list=True)
        if len(result) == 1:
            if ParserContext.INVALID_REQUEST_STATUS_VALUE != ParserContext.PARSER_RAISE:
                if ";" in result[0]:
                    code, desc = result[0].split(";", 1)
                else:
                    code = result[0]
                    desc = ""
                rest = None
            else:
                raise ValueError
        elif len(result) == 2:
            code, desc = result
            rest = None
        elif len(result) == 3:
            code, desc, rest = result
        else:
            if ParserContext.INVALID_REQUEST_STATUS_VALUE != ParserContext.PARSER_RAISE:
                code, desc, rest = result[:3]
            else:
                raise ValueError

        if "\\" in code and ParserContext.INVALID_REQUEST_STATUS_VALUE in (ParserContext.PARSER_IGNORE, ParserContext.PARSER_FIX):
            code = code.replace("\\", "")
        elif ParserContext.INVALID_REQUEST_STATUS_VALUE == ParserContext.PARSER_RAISE:
            raise ValueError

        # Decoding required
        self.mValue = [code, desc, rest, ] if rest else [code, desc, ]


    # os - StringIO object
    def generate(self, os):
        utils.generateTextList(os, self.mValue if len(self.mValue) < 3 or self.mValue[2] else self.mValue[:2])


    def writeXML(self, node, namespace):
        code = XML.SubElement(node, xmlutils.makeTag(namespace, xmldefinitions.req_status_code))
        code.text = self.mValue[0]

        description = XML.SubElement(node, xmlutils.makeTag(namespace, xmldefinitions.req_status_description))
        description.text = self.mValue[1]

        if len(self.mValue) == 3 and self.mValue[2]:
            data = XML.SubElement(node, xmlutils.makeTag(namespace, xmldefinitions.req_status_data))
            data.text = self.mValue[1]


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value

Value.registerType(Value.VALUETYPE_REQUEST_STATUS, RequestStatusValue, None)
