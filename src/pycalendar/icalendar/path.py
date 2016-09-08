##
#    Copyright (c) 2015 Cyrus Daboo. All rights reserved.
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

from urlparse import unquote

from pycalendar import stringutils
from pycalendar.componentbase import ComponentBase
from pycalendar.datetime import DateTime
from pycalendar.icalendar.componentrecur import ComponentRecur
from pycalendar.icalendar.property import Property


class Path(object):
    """
    A path item used to select one or more iCalendar elements
    """

    def __init__(self, path):
        """
        Create a L{Path} by parsing a text path.

        @param path: the path to parse
        @type path: L{str}
        """
        self.components = []
        self.property = None
        self.parameter = None
        self.value = None
        self._parsePath(path)

    def __str__(self):
        path = "".join(map(str, self.components))
        if self.property:
            path += str(self.property)
            if self.parameter:
                path += str(self.parameter)
            if self.value:
                path += "=" + self.value
        return path

    def targetComponent(self):
        """
        Indicate whether the path targets a component.

        @return: L{True} for a component target, L{False} otherwise.
        @rtype: L{bool}
        """
        return self.property is None

    def targetProperty(self):
        """
        Indicate whether the path targets a property.

        @return: L{True} for a property target, L{False} otherwise.
        @rtype: L{bool}
        """
        return (
            self.property is not None and
            self.parameter is None and
            self.value is None
        )

    def targetParameter(self):
        """
        Indicate whether the path targets a parameter.

        @return: L{True} for a parameter target, L{False} otherwise.
        @rtype: L{bool}
        """
        return (
            self.property is not None and
            self.parameter is not None and
            self.value is None
        )

    def targetPropertyValue(self):
        """
        Indicate whether the path targets a property.

        @return: L{True} for a property target, L{False} otherwise.
        @rtype: L{bool}
        """
        return (
            self.property is not None and
            self.parameter is None and
            self.value is not None
        )

    def targetParameterValue(self):
        """
        Indicate whether the path targets a parameter.

        @return: L{True} for a parameter target, L{False} otherwise.
        @rtype: L{bool}
        """
        return (
            self.property is not None and
            self.parameter is not None and
            self.value is not None
        )

    def _parsePath(self, path):
        """
        Parse a text path into its constituent segments.

        @param path: the path to parse
        @type path: L{str}
        """

        rest = path
        while rest:
            if rest[0] == "/":
                # Parse a component
                compname, rest = stringutils.strduptokenstr(rest[1:], "/#")
                self.components.append(Path.ComponentSegment(compname))
            elif rest[0] == "#":
                # Parse a property
                propname, rest = stringutils.strduptokenstr(rest[1:], "[;=")
                propmatch = None
                if rest and rest[0] == "[":
                    propmatch, rest = stringutils.strduptokenstr(rest[1:], "]")
                    rest = rest[1:]
                self.property = Path.PropertySegment(propname, propmatch)
            elif rest[0] == ";":
                # Can only follow a property
                if self.property is None:
                    raise ValueError("Invalid path: {}".format(path))
                # Parse a parameter
                paramname, rest = stringutils.strduptokenstr(rest[1:], "=")
                self.parameter = Path.ParameterSegment(paramname)
            elif rest[0] == "=":
                # Can only follow a property or parameter
                if self.property is None and self.parameter is None:
                    raise ValueError("Invalid path: {}".format(path))
                # Parse a value
                self.value = rest[1:]
                rest = None
            else:
                raise ValueError("Invalid path: {}".format(path))

    class ComponentSegment(object):
        """
        Represents a component segment of an L{Path}.
        """

        def __init__(self, segment):
            """
            Create a component segment of a path by parsing the text.

            @param path: the segment to parse
            @type path: L{str}
            """
            self.name = None
            self.uid = None
            self.rid = None
            self.rid_value = None

            self._parseSegment(segment)

        def __str__(self):
            path = "/" + self.name
            if self.uid:
                path += "[UID={}]".format(self.uid.replace("]", "%5D"))
            if self.rid:
                path += "[RID={}]".format(self.rid_value if self.rid_value is not None else "M")
            return path

        def __repr__(self):
            return "<ComponentSegment: {name}[{uid}][{rid}]".format(
                name=self.name,
                uid=self.uid,
                rid=(self.rid_value if self.rid_value is not None else "M") if self.rid else None
            )

        def __eq__(self, other):
            return (self.name == other.name) and \
                (self.uid == other.uid) and \
                (self.rid == other.rid) and \
                (self.rid_value == other.rid_value)

        def _parseSegment(self, segment):
            """
            Parse a component segment of a path into its constituent parts.

            @param path: the segment to parse
            @type path: L{str}
            """
            pos = segment.find("[")
            if pos != -1:
                self.name, segment_rest = segment.split("[", 1)
                segments = segment_rest.split("[")
                if segments[0].startswith("UID=") and segments[0][-1] == "]":
                    self.uid = unquote(segments[0][4:-1])
                    del segments[0]
                if segments and segments[0].startswith("RID=") and segments[0][-1] == "]":
                    rid = unquote(segments[0][4:-1])
                    if rid == "M":
                        self.rid_value = None
                    else:
                        try:
                            self.rid_value = DateTime.parseText(rid) if rid else None
                        except ValueError:
                            raise ValueError("Invalid component match {}".format(segment))
                    self.rid = True
                    del segments[0]

                if segments:
                    raise ValueError("Invalid component match {}".format(segment))
            else:
                self.name = segment

            self.name = self.name.upper()

        def match(self, items):
            """
            Returns all sub-components of the components passed in via the L{items} list
            that match this path.

            @param items: calendar items to match
            @type items: L{list}

            @return: items matched
            @rtype: L{list}
            """

            results = []
            for item in items:
                assert(isinstance(item, ComponentBase))
                matches = item.getComponents(self.name)
                if self.uid and matches:
                    matches = [item for item in matches if item.getUID() == self.uid]
                if self.rid and matches:
                    # self.rid is None if no RID= appears in the path.
                    # self.rid_value is None if RID= appears with no value - match the master instance
                    # Otherwise match the specific self.rid value.
                    rid_matches = [item for item in matches if isinstance(item, ComponentRecur) and item.getRecurrenceID() == self.rid_value]
                    if len(rid_matches) == 0:
                        if self.rid_value:
                            # Try deriving an instance - fail if cannot
                            # Need to have the master first
                            masters = [item for item in matches if isinstance(item, ComponentRecur) and item.getRecurrenceID() is None]
                            if not masters:
                                raise ValueError("No master component for path {}".format(self))
                            elif len(masters) > 1:
                                raise ValueError("Too many master components for path {}".format(self))
                            derived = masters[0].deriveComponent(self.rid_value)
                            masters[0].getParentComponent().addComponent(derived)
                            rid_matches.append(derived)
                    matches = rid_matches
                results.extend(matches)

            return results

    class PropertySegment(object):
        """
        Represents a property segment of an L{Path}.
        """

        def __init__(self, segment, match=None):
            """
            Create a property segment of a path by parsing the text.

            @param path: the segment to parse
            @type path: L{str}
            """
            self.name = None
            self.matchCondition = None
            self._parseSegment(segment, match)

        def __str__(self):
            path = "#" + self.name
            if self.matchCondition:
                if self.matchCondition[0] in "=!":
                    path += "[{}{}]".format(
                        self.matchCondition[0],
                        self.matchCondition[1].replace("]", "%5D"),
                    )
                elif self.matchCondition[0] == "@":
                    if self.matchCondition[2] is None:
                        path += "[{}{}]".format(
                            self.matchCondition[0],
                            self.matchCondition[1].replace("]", "%5D"),
                        )
                    else:
                        path += "[{}{}{}{}]".format(
                            self.matchCondition[0],
                            self.matchCondition[1],
                            self.matchCondition[2],
                            self.matchCondition[3].replace("]", "%5D"),
                        )
            return path

        def __repr__(self):
            return "<PropertySegment: {s.name}[{s.matchCondition}]".format(s=self)

        def __eq__(self, other):
            return (self.name == other.name) and \
                (self.matchCondition == other.matchCondition)

        def _parseSegment(self, segment, match):
            """
            Parse a property segment of a path into its constituent parts.

            @param path: the segment to parse
            @type path: L{str}
            """
            self.name = segment
            if match is not None:
                if len(match) > 1 and match[0] in "=!@":
                    if match[0] in "=!":
                        self.matchCondition = (match[0], unquote(match[1:]),)
                    else:
                        if "=" in match:
                            match, mvalue = match.split("=", 1)
                            self.matchCondition = (match[0], match[1:], "=", unquote(mvalue),)
                        elif "!" in match:
                            match, mvalue = match.split("!", 1)
                            self.matchCondition = (match[0], match[1:], "!", unquote(mvalue),)
                        else:
                            self.matchCondition = (match[0], match[1:], None, None,)
                else:
                    raise ValueError("Invalid property match {}".format(segment))

            if not self.name:
                raise ValueError("Invalid property match - name required {}".format(segment))

        @staticmethod
        def _op_eq(prop, match):
            return prop.getValue().getTextValue() == match

        @staticmethod
        def _op_ne(prop, match):
            return prop.getValue().getTextValue() != match

        @staticmethod
        def _op_param(prop, match):
            return prop.hasParameter(match)

        @staticmethod
        def _op_param_eq(prop, match):
            return prop.hasParameter(match[0]) and prop.getParameterValue(match[0]) == match[1]

        @staticmethod
        def _op_param_ne(prop, match):
            return not prop.hasParameter(match[0]) or prop.getParameterValue(match[0]) != match[1]

        def match(self, components, for_update):
            """
            Returns all properties of the components passed in via the L{items} list
            that match this path.

            @param components: components to match
            @type components: L{list}

            @return: items matched
            @rtype: L{list}
            """

            # Create function callables and data for matching
            if self.matchCondition:
                if self.matchCondition[0] == "=":
                    matcher = Path.PropertySegment._op_eq
                    match = self.matchCondition[1]
                elif self.matchCondition[0] == "!":
                    matcher = Path.PropertySegment._op_ne
                    match = self.matchCondition[1]
                elif self.matchCondition[0] == "@":
                    if self.matchCondition[2] == "=":
                        match = (self.matchCondition[1], self.matchCondition[3])
                        matcher = Path.PropertySegment._op_param_eq
                    elif self.matchCondition[2] == "!":
                        match = (self.matchCondition[1], self.matchCondition[3])
                        matcher = Path.PropertySegment._op_param_ne
                    else:
                        match = self.matchCondition[1]
                        matcher = Path.PropertySegment._op_param

            results = []
            for component in components:
                assert(isinstance(component, ComponentBase))
                if self.matchCondition is not None:
                    matches = [(component, prop,) for prop in component.getProperties(self.name) if matcher(prop, match)]
                else:
                    matches = [(component, prop,) for prop in component.getProperties(self.name)]
                    if len(matches) == 0 and for_update:
                        # If no property exists, return L{None} so that an update action will add one
                        matches = [(component, None)]
                results.extend(matches)

            return results

    class ParameterSegment(object):
        """
        Represents a parameter segment of an L{Path}.
        """

        def __init__(self, segment):
            """
            Create a parameter segment of a path by parsing the text.

            @param path: the segment to parse
            @type path: L{str}
            """
            self.name = None
            self._parseSegment(segment)

        def __str__(self):
            path = ";" + self.name
            return path

        def __repr__(self):
            return "<ParameterSegment: {s.name}".format(s=self)

        def __eq__(self, other):
            return (self.name == other.name)

        def _parseSegment(self, segment):
            """
            Parse a parameter segment of a path into its constituent parts.

            @param path: the segment to parse
            @type path: L{str}
            """
            if "[" in segment:
                raise ValueError("Invalid parameter segment {}".format(segment))
            else:
                self.name = segment
            if not self.name:
                raise ValueError("Invalid parameter match - name required {}".format(segment))

        def match(self, properties):
            """
            Returns all properties of the components passed in via the L{items} list
            that match this path, together with the parameter name being targeted.

            @param properties: properties to match
            @type properties: L{list}

            @return: items matched
            @rtype: L{list}
            """

            results = []
            for component, property in properties:
                assert(isinstance(component, ComponentBase))
                assert(isinstance(property, Property))
                results.append((component, property, self.name,))

            return results

    def match(self, calendar, for_update=False):
        """
        Return the list of matching items in the specified calendar.

        @param calendar: calendar to match
        @type calendar: L{Calendar}
        @param for_update: L{True} if a property match should return an empty
            result when there is no match item and no matching property
        @type for_update: L{bool}

        @return: items matched
        @rtype: L{list}
        """

        # Absolute path starts with VCALENDAR - we double check that
        start_segment = 0
        if self.components and self.components[0].name == "VCALENDAR":
            if calendar.getType().upper() == "VCALENDAR":
                # Skip the first segment since we know it matches
                start_segment = 1
            else:
                return []

        # Start with the root object as the initial match
        results = [calendar]
        for component_segment in self.components[start_segment:]:
            results = component_segment.match(results)

        if self.property is not None:
            results = self.property.match(results, for_update)
            if self.parameter is not None:
                results = self.parameter.match(results)

        return results
