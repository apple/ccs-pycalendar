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
from pycalendar.componentbase import ComponentBase
from pycalendar.exceptions import InvalidData, ValidationError
from pycalendar.parser import ParserContext
from pycalendar.utils import readFoldedLine
import json

class ContainerBase(ComponentBase):
    """
    Represents the top-level component (i.e., VCALENDAR or vCARD)
    """

    sProdID = "-//mulberrymail.com//Mulberry v4.0//EN"
    sDomain = "mulberrymail.com"

    # These must be set by derived classes
    sContainerDescriptor = None
    sComponentType = None
    sPropertyType = None

    @classmethod
    def setPRODID(cls, prodid):
        cls.sProdID = prodid


    @classmethod
    def setDomain(cls, domain):
        cls.sDomain = domain


    def __init__(self, add_defaults=True):
        super(ContainerBase, self).__init__()

        if add_defaults:
            self.addDefaultProperties()


    def duplicate(self):
        return super(ContainerBase, self).duplicate()


    def getType(self):
        raise NotImplementedError


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
        fixed, unfixed = super(ContainerBase, self).validate(doFix)
        if doRaise and unfixed:
            raise ValidationError(";".join(unfixed))
        return fixed, unfixed


    @classmethod
    def parseText(cls, data):

        cal = cls(add_defaults=False)
        if cal.parse(StringIO(data)):
            return cal
        else:
            return None


    def parse(self, ins):

        result = False

        self.setProperties({})

        LOOK_FOR_CONTAINER = 0
        GET_PROPERTY_OR_COMPONENT = 1

        state = LOOK_FOR_CONTAINER

        # Get lines looking for start of calendar
        lines = [None, None]
        comp = self
        compend = None
        componentstack = []

        while readFoldedLine(ins, lines):

            line = lines[0]

            if state == LOOK_FOR_CONTAINER:

                # Look for start
                if line == self.getBeginDelimiter():
                    # Next state
                    state = GET_PROPERTY_OR_COMPONENT

                    # Indicate success at this point
                    result = True

                # Handle blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise InvalidData("%s data has blank lines" % (self.sContainerDescriptor,))

                # Unrecognized data
                else:
                    raise InvalidData("%s data not recognized" % (self.sContainerDescriptor,), line)

            elif state == GET_PROPERTY_OR_COMPONENT:

                # Parse property or look for start of component
                if line.startswith("BEGIN:") and self.sComponentType is not None:

                    # Push previous details to stack
                    componentstack.append((comp, compend,))

                    # Start a new component
                    comp = self.sComponentType.makeComponent(line[6:], comp)
                    compend = comp.getEndDelimiter()

                # Look for end of object
                elif line == self.getEndDelimiter():

                    # Finalise the current calendar
                    self.finalise()

                    # Change state
                    state = LOOK_FOR_CONTAINER

                # Look for end of current component
                elif line == compend:

                    # Finalise the component (this caches data from the properties)
                    comp.finalise()

                    # Embed component in parent and reset to use parent
                    componentstack[-1][0].addComponent(comp)
                    comp, compend = componentstack.pop()

                # Blank line
                elif len(line) == 0:
                    # Raise if requested, otherwise just ignore
                    if ParserContext.BLANK_LINES_IN_DATA == ParserContext.PARSER_RAISE:
                        raise InvalidData("%s data has blank lines" % (self.sContainerDescriptor,))

                # Must be a property
                else:

                    # Parse parameter/value for top-level calendar item
                    prop = self.sPropertyType.parseText(line)

                    # Check for valid property
                    if comp is self:
                        if not comp.validProperty(prop):
                            raise InvalidData("Invalid property", str(prop))
                        else:
                            comp.addProperty(prop)
                    else:
                        comp.addProperty(prop)

        # Check for truncated data
        if state != LOOK_FOR_CONTAINER:
            raise InvalidData("%s data not complete" % (self.sContainerDescriptor,))

        # Validate some things
        if result and not self.hasProperty("VERSION"):
            raise InvalidData("%s missing VERSION" % (self.sContainerDescriptor,))

        return result


    @classmethod
    def parseJSONText(cls, data):

        try:
            return cls.parseJSON(json.loads(data), None, cls(add_defaults=False))
        except Exception:
            return None


    def getTextJSON(self):
        jobject = []
        self.writeJSON(jobject)
        return json.dumps(jobject[0], indent=2, separators=(',', ':'))


    def addDefaultProperties(self):
        raise NotImplementedError


    def validProperty(self, prop):
        raise NotImplementedError
