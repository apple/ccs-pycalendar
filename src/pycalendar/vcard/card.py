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

from cStringIO import StringIO
from pycalendar.componentbase import PyCalendarComponentBase
from pycalendar.exceptions import PyCalendarInvalidData, \
    PyCalendarValidationError
from pycalendar.parser import ParserContext
from pycalendar.utils import readFoldedLine
from pycalendar.vcard import definitions
from pycalendar.vcard.definitions import VCARD, Property_VERSION, \
    Property_PRODID, Property_UID
from pycalendar.vcard.property import Property
from pycalendar.vcard.validation import VCARD_VALUE_CHECKS

class Card(PyCalendarComponentBase):

    sProdID = "-//mulberrymail.com//Mulberry v4.0//EN"
    sDomain = "mulberrymail.com"

    @staticmethod
    def setPRODID(prodid):
        Card.sProdID = prodid


    @staticmethod
    def setDomain(domain):
        Card.sDomain = domain

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

    def __init__(self, add_defaults=True):
        super(Card, self).__init__()

        if add_defaults:
            self.addDefaultProperties()


    def duplicate(self):
        return super(Card, self).duplicate()


    def getType(self):
        return VCARD


    def finalise(self):
        pass


    def validate(self, doFix=False, doRaise=False):
        """
        Validate the data in this component and optionally fix any problems. Return
        a tuple containing two lists: the first describes problems that were fixed, the
        second problems that were not fixed. Caller can then decide what to do with unfixed
        issues.
        """

        # Optional raise behavior
        fixed, unfixed = super(Card, self).validate(doFix)
        if doRaise and unfixed:
            raise PyCalendarValidationError(";".join(unfixed))
        return fixed, unfixed


    def sortedPropertyKeyOrder(self):
        return (
            Property_VERSION,
            Property_PRODID,
            Property_UID,
        )


    @staticmethod
    def parseMultiple(ins):

        results = []

        card = Card(add_defaults=False)

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
                        raise PyCalendarInvalidData("vCard data has blank lines")

                # Unrecognized data
                else:
                    raise PyCalendarInvalidData("vCard data not recognized", line)

            elif state == GET_PROPERTY:

                # Look for end of object
                if line == card.getEndDelimiter():

                    # Finalise the current calendar
                    card.finalise()

                    # Validate some things
                    if not card.hasProperty("VERSION"):
                        raise PyCalendarInvalidData("vCard missing VERSION", "")

                    results.append(card)

                    # Change state
                    card = Card(add_defaults=False)
                    state = LOOK_FOR_VCARD

                # Blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise PyCalendarInvalidData("vCard data has blank lines")

                # Must be a property
                else:

                    # Parse attribute/value for top-level calendar item
                    prop = Property()
                    if prop.parse(line):

                        # Check for valid property
                        if not card.validProperty(prop):
                            raise PyCalendarInvalidData("Invalid property", str(prop))
                        else:
                            card.addProperty(prop)

        # Check for truncated data
        if state != LOOK_FOR_VCARD:
            raise PyCalendarInvalidData("vCard data not complete")

        return results


    @staticmethod
    def parseText(data):

        cal = Card(add_defaults=False)
        if cal.parse(StringIO(data)):
            return cal
        else:
            return None


    def parse(self, ins):

        result = False

        self.setProperties({})

        LOOK_FOR_VCARD = 0
        GET_PROPERTY = 1

        state = LOOK_FOR_VCARD

        # Get lines looking for start of calendar
        lines = [None, None]

        while readFoldedLine(ins, lines):

            line = lines[0]
            if state == LOOK_FOR_VCARD:

                # Look for start
                if line == self.getBeginDelimiter():
                    # Next state
                    state = GET_PROPERTY

                    # Indicate success at this point
                    result = True

                # Handle blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise PyCalendarInvalidData("vCard data has blank lines")

                # Unrecognized data
                else:
                    raise PyCalendarInvalidData("vCard data not recognized", line)

            elif state == GET_PROPERTY:

                # Look for end of object
                if line == self.getEndDelimiter():

                    # Finalise the current calendar
                    self.finalise()

                    # Change state
                    state = LOOK_FOR_VCARD

                # Blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise PyCalendarInvalidData("vCard data has blank lines")

                # Must be a property
                else:

                    # Parse attribute/value for top-level calendar item
                    prop = Property()
                    try:
                        if prop.parse(line):

                            # Check for valid property
                            if not self.validProperty(prop):
                                raise PyCalendarInvalidData("Invalid property", str(prop))
                            else:
                                self.addProperty(prop)
                    except IndexError:
                        print line

        # Check for truncated data
        if state != LOOK_FOR_VCARD:
            raise PyCalendarInvalidData("vCard data not complete", "")

        # Validate some things
        if result and not self.hasProperty("VERSION"):
            raise PyCalendarInvalidData("vCard missing VERSION", "")

        return result


    def addDefaultProperties(self):
        self.addProperty(Property(definitions.Property_PRODID, Card.sProdID))
        self.addProperty(Property(definitions.Property_VERSION, "3.0"))


    def validProperty(self, prop):
        if prop.getName() == definitions.Property_VERSION:

            tvalue = prop.getValue()
            if ((tvalue is None) or (tvalue.getValue() != "3.0")):
                return False

        return True
