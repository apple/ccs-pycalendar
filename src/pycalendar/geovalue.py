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

from pycalendar import xmlutils
from pycalendar.exceptions import InvalidData
from pycalendar.icalendar import xmldefinitions
from pycalendar.value import Value
from pycalendar import xmldefinitions as xmldefinitions_top
import xml.etree.cElementTree as XML

class GeoValue(Value):
    """
    The value is a list of 2 floats
    """

    def __init__(self, value=None):
        self.mValue = value if value is not None else [0.0, 0.0]


    def __hash__(self):
        return hash(tuple(self.mValue))


    def duplicate(self):
        return GeoValue(self.mValue[:])


    def getType(self):
        return Value.VALUETYPE_GEO


    def parse(self, data, variant="icalendar"):

        splits = data.split(";")
        if len(splits) != 2:
            raise InvalidData("GEO value incorrect", data)
        try:
            self.mValue = [float(splits[0]), float(splits[1])]
        except ValueError:
            if splits[0][-1] == '\\':
                try:
                    self.mValue = [float(splits[0][:-1]), float(splits[1])]
                except ValueError:
                    raise InvalidData("GEO value incorrect", data)
            else:
                raise InvalidData("GEO value incorrect", data)


    # os - StringIO object
    def generate(self, os):
        os.write("%s;%s" % (self.mValue[0], self.mValue[1],))


    def writeXML(self, node, namespace):
        value = self.getXMLNode(node, namespace)

        latitude = XML.SubElement(value, xmlutils.makeTag(namespace, xmldefinitions.geo_latitude))
        latitude.text = self.mValue[0]

        longitude = XML.SubElement(value, xmlutils.makeTag(namespace, xmldefinitions.geo_longitude))
        longitude.text = self.mValue[1]


    def parseJSONValue(self, jobject):
        self.mValue = jobject


    def writeJSONValue(self, jobject):
        jobject.append(list(self.mValue))


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value

Value.registerType(Value.VALUETYPE_GEO, GeoValue, xmldefinitions.geo, xmldefinitions_top.value_float)
