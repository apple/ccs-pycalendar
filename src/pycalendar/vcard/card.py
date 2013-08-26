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

from cStringIO import StringIO
from pycalendar.containerbase import ContainerBase
from pycalendar.exceptions import InvalidData
from pycalendar.parser import ParserContext
from pycalendar.utils import readFoldedLine
from pycalendar.vcard import definitions
from pycalendar.vcard.definitions import VCARD, Property_VERSION, \
    Property_PRODID, Property_UID
from pycalendar.vcard.property import Property
from pycalendar.vcard.validation import VCARD_VALUE_CHECKS
import json

class Card(ContainerBase):

    sContainerDescriptor = "vCard"
    sComponentType = None
    sPropertyType = Property

    sFormatText = "text/vcard"
    sFormatJSON = "application/vcard+json"

    propertyCardinality_1 = (
        definitions.Property_VERSION,
        definitions.Property_N,
    )

    propertyCardinality_0_1 = (
        definitions.Property_BDAY,
        definitions.Property_PRODID,
        definitions.Property_REV,
        definitions.Property_UID,
    )

    propertyCardinality_1_More = (
        definitions.Property_FN,
    )

    propertyValueChecks = VCARD_VALUE_CHECKS

    def duplicate(self):
        return super(Card, self).duplicate()


    def getType(self):
        return VCARD


    def sortedPropertyKeyOrder(self):
        return (
            Property_VERSION,
            Property_PRODID,
            Property_UID,
        )


    @classmethod
    def parseMultipleData(cls, data, format):

        if format == cls.sFormatText:
            return cls.parseMultipleTextData(data)
        elif format == cls.sFormatJSON:
            return cls.parseMultipleJSONData(data)


    @classmethod
    def parseMultipleTextData(cls, ins):

        if isinstance(ins, str):
            ins = StringIO(ins)

        results = []

        card = cls(add_defaults=False)

        LOOK_FOR_VCARD = 0
        GET_PROPERTY = 1

        state = LOOK_FOR_VCARD

        # Get lines looking for start of calendar
        lines = [None, None]

        while readFoldedLine(ins, lines):

            line = lines[0]
            if state == LOOK_FOR_VCARD:

                # Look for start
                if line == card.getBeginDelimiter():
                    # Next state
                    state = GET_PROPERTY

                # Handle blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise InvalidData("vCard data has blank lines")

                # Unrecognized data
                else:
                    raise InvalidData("vCard data not recognized", line)

            elif state == GET_PROPERTY:

                # Look for end of object
                if line == card.getEndDelimiter():

                    # Finalise the current calendar
                    card.finalise()

                    # Validate some things
                    if not card.hasProperty("VERSION"):
                        raise InvalidData("vCard missing VERSION", "")

                    results.append(card)

                    # Change state
                    card = Card(add_defaults=False)
                    state = LOOK_FOR_VCARD

                # Blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise InvalidData("vCard data has blank lines")

                # Must be a property
                else:

                    # Parse parameter/value for top-level calendar item
                    prop = Property.parseText(line)

                    # Check for valid property
                    if not card.validProperty(prop):
                        raise InvalidData("Invalid property", str(prop))
                    else:
                        card.addProperty(prop)

        # Check for truncated data
        if state != LOOK_FOR_VCARD:
            raise InvalidData("vCard data not complete")

        return results


    @classmethod
    def parseMultipleJSONData(cls, data):

        if not isinstance(data, str):
            data = data.read()
        try:
            jobjects = json.loads(data)
        except ValueError, e:
            raise InvalidData(e, data)
        results = []
        for jobject in jobjects:
            results.append(cls.parseJSON(jobject, None, cls(add_defaults=False)))
        return results


    def addDefaultProperties(self):
        self.addProperty(Property(definitions.Property_PRODID, Card.sProdID))
        self.addProperty(Property(definitions.Property_VERSION, "3.0"))


    def validProperty(self, prop):
        if prop.getName() == definitions.Property_VERSION:

            tvalue = prop.getValue()
            if ((tvalue is None) or (tvalue.getValue() != "3.0")):
                return False

        return True
