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

from calendar import Calendar
from collections import Counter
from pycalendar.componentbase import ComponentBase
from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.componentrecur import ComponentRecur
from pycalendar.icalendar.patch import Patch
from pycalendar.icalendar.property import Property
from pycalendar.icalendar.vpatch import VPatch
from pycalendar.parameter import Parameter
from urlparse import unquote
import operator


class PatchDocument(object):
    """
    Represents an entire patch document by maintaining a list of all its commands.
    """

    def __init__(self, calendar=None):
        self.commands = []
        if calendar is not None:
            self.parsePatch(calendar)

    def parsePatch(self, calendar):
        """
        Parse an iCalendar object and extract all the VPATCH components in the
        proper order and parse them as a set of commands to use when applying
        the patch.

        @param calendar: iCalendar object to parse
        @type calendar: L{Calendar}
        """

        # Get all VPATCH components
        vpatches = calendar.getComponents(definitions.cICalComponent_VPATCH)

        # Sort
        def _vpatchOrder(component):
            return component.loadValueInteger(definitions.cICalProperty_PATCH_ORDER)
        vpatches = sorted(vpatches, key=_vpatchOrder)

        # Extract commands from each VPATCH
        for vpatch in vpatches:
            for component in vpatch.getComponents():
                if component.getType().upper() != definitions.cICalComponent_PATCH:
                    raise ValueError("Invalid component in VPATCH: {}".format(component.getType().upper()))
                commands = Command.parseFromComponent(component)
                self.commands.extend(commands)

        # Validate
        self.validate()

    def validate(self):
        """
        Validate all the commands.
        """
        for command in self.commands:
            command.validate()

    def applyPatch(self, calendar):
        """
        Apply the patch to the specified calendar. The supplied L{Calendar} object will be
        changed in place.

        @param calendar: calendar to patch
        @type calendar: L{Calendar}
        """
        for command in self.commands:
            command.applyPatch(calendar)


class Command(object):
    """
    Represents a patch document command.
    """

    def __init__(self):
        self.path = None
        self.deletes = None
        self.params = None
        self.data = None

    @classmethod
    def create(cls, path, deletes=None, params=None, data=None):
        if isinstance(path, str):
            path = Path(path)
        elif not isinstance(path, Path):
            raise ValueError("Invalid path: {}".format(path))
        if deletes is not None and not isinstance(deletes, list):
            raise ValueError("Invalid deletes: {}".format(deletes))
        if params is not None and not isinstance(params, list):
            raise ValueError("Invalid params: {}".format(params))
        if data is not None and not isinstance(data, Component):
            raise ValueError("Invalid data: {}".format(data))

        command = Command()
        command.path = path
        command.params = params
        command.deletes = deletes
        command.data = data
        return command

    @classmethod
    def parseFromComponent(cls, component):
        """
        Parse a command from a list of text format lines.

        @param component: PATCH component to process.
        @type component: L{Component}

        @return: L{Command} if a command was parsed, L{None} if not
        """

        # Get the action from the component type
        if component.getType().upper() != definitions.cICalComponent_PATCH:
            raise ValueError("Invalid component: {}".format(component.getType().upper()))

        # Need to extract the sub-components and properties being processed, so dup the original
        # component so we can remove the unwanted PATCH- items from it
        data = component.duplicate()

        # Process the PATCH-TARGET property
        targets = component.getProperties(definitions.cICalProperty_PATCH_TARGET)
        if len(targets) != 1:
            raise ValueError("Must have one PATCH-TARGET property in PATCH component")
        target = component.getPropertyString(definitions.cICalProperty_PATCH_TARGET)
        try:
            path = Path(target)
        except ValueError:
            raise ValueError("Invalid target path: {}".format(target))
        data.removeProperties(definitions.cICalProperty_PATCH_TARGET)

        # Process any PATCH-DELETE properties
        deletes = [
            Path(target + delete.getTextValue().getValue())
            for delete in data.getProperties(definitions.cICalProperty_PATCH_DELETE)
        ]
        data.removeProperties(definitions.cICalProperty_PATCH_DELETE)

        # Process any PATCH-PARAMETER properties
        params = [
            (Path(target + param.getTextValue().getValue()), param.getParameters(),)
            for param in data.getProperties(definitions.cICalProperty_PATCH_PARAMETER)
        ]
        data.removeProperties(definitions.cICalProperty_PATCH_PARAMETER)

        return (Command.create(path, deletes, params, data), )

    def validate(self):
        """
        Make sure the semantics of the patch are correct based on the supplied data etc.
        """

        if self.path.targetComponent():
            # Data must be one or more components only
            if len(self.data.getProperties()) + len(self.data.getComponents()) + len(self.deletes) + len(self.params) == 0:
                raise ValueError("patch must include at least one property or component: {}".format(self.path))

            # Deletes must be proper paths
            for delete in self.deletes:
                if not delete.targetComponent() and not delete.targetProperty() and not delete.targetParameter():
                    raise ValueError("delete action path is not valid: {}".format(delete))

            # Params must be proper paths
            for path, params in self.params:
                if not path.targetProperty() and not path.targetParameter():
                    raise ValueError("param action path is not valid: {}".format(path))
                if len(params) == 0:
                    raise ValueError("param action must have parameters: {}".format(path))
        else:
            raise ValueError("patch path is not valid: {}".format(self.path))

    def applyPatch(self, calendar):
        """
        Apply the patch to the specified calendar. The supplied L{Calendar} object will be
        changed in place.

        @param calendar: calendar to patch
        @type calendar: L{Calendar}
        """

        if self.path.targetComponent():
            matches = self.path.match(calendar)

            # Process all deletes first
            for dpath in self.deletes:
                self.processDelete(dpath, dpath.match(calendar))

            # Process all params second
            for ppath, params in self.params:
                self.processParameter(ppath, params, ppath.match(calendar))

            # Process sub-components and properties
            # Data is a list of components or properties
            for component in matches:
                self.processSubComponents(component)
                self.processProperties(component)

        else:
            raise ValueError("create action path is not valid: {}".format(self.path))

    def processDelete(self, path, matches):
        """
        Execute a delete action on the matched items.

        @param path: path being processed
        @type path: L{Path}
        @param matches: list of matched components/properties/parameters
        @type matches: L{list}
        """
        if path.targetComponent():
            for component in matches:
                component.removeFromParent()

        elif path.targetProperty():
            for component, property in matches:
                component.removeProperty(property)

        elif path.targetParameter():
            for _ignore_component, property, parameter_name in matches:
                property.removeParameters(parameter_name)

        else:
            raise ValueError("delete path is not valid: {}".format(path))

    def processSubComponents(self, component):
        """
        Process sub-components for matched component.

        @param component: component to process
        @type component: L{Component}
        """

        for newcomponent in self.data.getComponents():
            mapkey = newcomponent.getMapKey()
            component.removeComponentByKey(mapkey)
            component.addComponent(newcomponent.duplicate(parent=component))

    def processProperties(self, component):
        """
        Process properties for matched components.

        @param component: component to process
        @type component: L{Component}
        """
        for newpropertylist in self.data.getProperties().values():
            for newproperty in newpropertylist:
                if newproperty.hasParameter(definitions.cICalParameter_PATCH_ACTION):
                    action = newproperty.getParameterValue(definitions.cICalParameter_PATCH_ACTION)
                    newproperty.removeParameters(definitions.cICalParameter_PATCH_ACTION)
                else:
                    action = None

                # Always replace
                if action is None:
                    component.removeProperties(newproperty.getName())
                    component.addProperty(newproperty.duplicate())

                # Just add
                elif action == definitions.cICalParameter_PATCH_ACTION_CREATE:
                    component.addProperty(newproperty.duplicate())

                # Replace property with the same value
                elif action == definitions.cICalParameter_PATCH_ACTION_BYVALUE:
                    oldprops = component.getProperties(newproperty.getName())
                    newvalue = newproperty.getValue()
                    for oldprop in oldprops:
                        if oldprop.getValue() == newvalue:
                            component.removeProperty(oldprop)
                    component.addProperty(newproperty.duplicate())

                # Replace property with the same param value
                elif action.startswith(definitions.cICalParameter_PATCH_ACTION_BYPARAM):
                    parammatch = action.split(";", 1)[1]
                    paramname, paramvalue = parammatch.split("=", 1)
                    oldprops = component.getProperties(newproperty.getName())
                    for oldprop in oldprops:
                        if oldprop.hasParameter(paramname) and paramvalue in oldprop.getParameterValues():
                            component.removeProperty(oldprop)
                    component.addProperty(newproperty.duplicate())

    def processParameter(self, path, params, matches):
        """
        Execute a parameter action on the matched items.

        @param path: path being processed
        @type path: L{Path}
        @param params: parameters to add to property
        @type params: L{dict}
        @param matches: list of matched components/properties/parameters
        @type matches: L{list}
        """
        if path.targetProperty():
            for _ignore_component, property in matches:
                for parameters in params.values():
                    # Remove existing, then add
                    if property.hasParameter(parameters[0].getName()):
                        property.removeParameters(parameters[0].getName())
                    property.addParameter(parameters[0].duplicate())

        elif path.targetParameter():
            for _ignore_component, property, _ignore_parameter in matches:
                for parameters in params.values():
                    # Remove existing, then add
                    if property.hasParameter(parameters[0].getName()):
                        property.removeParameters(parameters[0].getName())
                    property.addParameter(parameters[0].duplicate())

        else:
            raise ValueError("params path is not valid: {}".format(path))


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
        self._parsePath(path)

    def __str__(self):
        path = "".join(map(str, self.components))
        if self.property:
            path += str(self.property)
            if self.parameter:
                path += str(self.parameter)
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
            self.parameter is None
        )

    def targetParameter(self):
        """
        Indicate whether the path targets a parameter.

        @return: L{True} for a parameter target, L{False} otherwise.
        @rtype: L{bool}
        """
        return (
            self.property is not None and
            self.parameter is not None
        )

    def _parsePath(self, path):
        """
        Parse a text path into its constituent segments.

        @param path: the path to parse
        @type path: L{str}
        """

        segments = path.split("/")
        property_segment = None
        parameter_segment = None
        if segments[0] != "":
            raise ValueError("Invalid path: {}".format(path))
        del segments[0]
        if "#" in segments[-1]:
            segments[-1], property_segment = segments[-1].split("#", 1)
            if ";" in property_segment:
                property_segment, parameter_segment = property_segment.split(";", 1)

        for item in range(len(segments)):
            self.components.append(Path.ComponentSegment(segments[item]))
        if property_segment is not None:
            self.property = Path.PropertySegment(property_segment)
        if parameter_segment is not None:
            self.parameter = Path.ParameterSegment(parameter_segment)

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
                path += "[UID={}]".format(self.uid)
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

        def __init__(self, segment):
            """
            Create a property segment of a path by parsing the text.

            @param path: the segment to parse
            @type path: L{str}
            """
            self.name = None
            self.matchCondition = None
            self._parseSegment(segment)

        def __str__(self):
            path = "#" + self.name
            if self.matchCondition:
                path += "[{}{}]".format("=" if self.matchCondition[1] == operator.eq else "!", self.matchCondition[0])
            return path

        def __repr__(self):
            return "<PropertySegment: {s.name}[{s.matchCondition}]".format(s=self)

        def __eq__(self, other):
            return (self.name == other.name) and \
                (self.matchCondition == other.matchCondition)

        def _parseSegment(self, segment):
            """
            Parse a property segment of a path into its constituent parts.

            @param path: the segment to parse
            @type path: L{str}
            """
            if "[" in segment:
                self.name, segment_rest = segment.split("[", 1)
                matches = segment_rest.split("[")
                if len(matches) != 1:
                    raise ValueError("Invalid property match {}".format(segment))
                if matches[0][-1] != "]" or len(matches[0]) < 4:
                    raise ValueError("Invalid property match {}".format(segment))
                if matches[0][0] == "=":
                    op = operator.eq
                elif matches[0][0] == "!":
                    op = operator.ne
                else:
                    raise ValueError("Invalid property match {}".format(segment))
                self.matchCondition = (unquote(matches[0][1:-1]), op,)
            else:
                self.name = segment
            if not self.name:
                raise ValueError("Invalid property match - name required {}".format(segment))

        def match(self, components, for_update):
            """
            Returns all properties of the components passed in via the L{items} list
            that match this path.

            @param components: components to match
            @type components: L{list}

            @return: items matched
            @rtype: L{list}
            """

            results = []
            for component in components:
                assert(isinstance(component, ComponentBase))
                if self.matchCondition is not None:
                    matches = [(component, prop,) for prop in component.getProperties(self.name) if self.matchCondition[1](prop.getValue().getTextValue(), self.matchCondition[0])]
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

        # First segment of path is always assumed to be VCALENDAR - we double check that
        if self.components[0].name != "VCALENDAR" or calendar.getType().upper() != "VCALENDAR":
            return []

        # Start with the VCALENDAR object as the initial match
        results = [calendar]
        for component_segment in self.components[1:]:
            results = component_segment.match(results)

        if self.property is not None:
            results = self.property.match(results, for_update)
            if self.parameter is not None:
                results = self.parameter.match(results)

        return results


class PatchGenerator(object):
    """
    Class that manages the creation of a VPATCH by diff'ing two components.
    """

    @staticmethod
    def createPatch(oldcalendar, newcalendar):
        """
        Create a patch iCelendar object for the difference between
        L{oldcalendar} and L{newcalendar}.

        @param oldcalendar: the old calendar data
        @type oldcalendar: L{Calendar}
        @param newcalendar: thew new calendar data
        @type newcalendar: L{Calendar}
        """

        # Create the VPATCH object
        patchcal = Calendar()
        vpatch = VPatch(parent=patchcal)
        vpatch.addDefaultProperties()
        patchcal.addComponent(vpatch)

        # Recursively traverse the differences between two components, adding
        # appropriate items to the VPATCH to describe the differences
        PatchGenerator.diffComponents(oldcalendar, newcalendar, vpatch, "")

        return patchcal

    @staticmethod
    def diffComponents(oldcomponent, newcomponent, vpatch, path):
        """
        Recursively traverse the differences between two components, adding
        appropriate items to the VPATCH to describe the differences.

        @param oldcomponent: the old component
        @type oldcomponent: L{Component}
        @param newcomponent: the new component
        @type newcomponent: L{Component}
        @param vpatch: the patch to use
        @type vpatch: L{VPatch}
        """

        # Update path to include this component
        path += "/{}".format(oldcomponent.getType())

        # Create a PATCH component - but don't add it until the end when we know
        # whether anything was added to it or not
        patchComponent = Patch(parent=vpatch)
        patchComponent.addProperty(Property(definitions.cICalProperty_PATCH_TARGET, path))

        # Process properties then sub-components
        PatchGenerator.processProperties(oldcomponent, newcomponent, vpatch, path, patchComponent)
        PatchGenerator.processSubComponents(oldcomponent, newcomponent, vpatch, path, patchComponent)

        if len(patchComponent.getProperties()) + len(patchComponent.getComponents()) > 1:
            vpatch.addComponent(patchComponent)

    @staticmethod
    def processProperties(oldcomponent, newcomponent, vpatch, path, patchComponent):
        """
        Determine the property differences between two components and create
        appropriate VPATCH entries.

        @param oldcomponent: the old component
        @type oldcomponent: L{Component}
        @param newcomponent: the new component
        @type newcomponent: L{Component}
        @param vpatch: the patch to use
        @type vpatch: L{VPatch}
        @param patchComponent: the PATCH component to add changes to
        @type patchComponent: L{Patch}
        """

        # Use two way set difference to find new and removed
        oldset = set(oldcomponent.getProperties().keys())
        newset = set(newcomponent.getProperties().keys())

        # New ones
        newpropnames = newset - oldset
        if len(newpropnames) != 0:
            # Add each property to PATCH. Note that if we are adding more than one we need to include
            # PATCH-ACTION=CREATE parameter on each one.
            for newpropname in newpropnames:
                actionRequired = len(newcomponent.getProperties(newpropname)) > 1
                for prop in newcomponent.getProperties(newpropname):
                    newprop = prop.duplicate()
                    if actionRequired:
                        newprop.addParameter(Parameter(definitions.cICalParameter_PATCH_ACTION, definitions.cICalParameter_PATCH_ACTION_CREATE))
                    patchComponent.addProperty(newprop)

        # Removed ones
        oldpropnames = oldset - newset
        if len(oldpropnames) != 0:
            # Add each property to a PATCH-DELETE
            for oldpropname in oldpropnames:
                patchComponent.addProperty(Property(definitions.cICalProperty_PATCH_DELETE, "#{}".format(oldpropname)))

        # Ones that exist in both old and new: this is tricky as we now need to find out what is different.
        # We handle two cases: single occurring properties vs multi-occurring
        checkpropnames = newset & oldset
        for propname in checkpropnames:
            oldprops = oldcomponent.getProperties(propname)
            newprops = newcomponent.getProperties(propname)

            # Look for singletons
            if len(oldprops) == 1 and len(newprops) == 1:
                # Check for difference
                if oldprops[0] != newprops[0]:
                    patchComponent.addProperty(newprops[0].duplicate())

            # Rest are multi-occurring
            else:
                # Removes ones that are exactly the same
                oldset = set(oldprops)
                newset = set(newprops)
                oldsetchanged = oldset - newset
                newsetchanged = newset - oldset

                # Need to check for ones that have the same value, but different parameters
                oldvalues = dict([(prop.getValue().getTextValue(), prop) for prop in oldsetchanged])
                newvalues = dict([(prop.getValue().getTextValue(), prop) for prop in newsetchanged])

                # Ones to remove by value (ones whose value only exists in the old set)
                for removeval in set(oldvalues.keys()) - set(newvalues.keys()):
                    patchComponent.addProperty(Property(definitions.cICalProperty_PATCH_DELETE, "#{}[={}]".format(propname, removeval)))

                # Ones to create (ones whose value only exists in the new set). Add as PATCH-ACTION=CREATE.
                for createval in set(newvalues.keys()) - set(oldvalues.keys()):
                    newprop = newvalues[createval].duplicate()
                    newprop.addParameter(Parameter(definitions.cICalParameter_PATCH_ACTION, definitions.cICalParameter_PATCH_ACTION_CREATE))
                    patchComponent.addProperty(newprop)

                # Ones with the same value - check if parameters are different. Add as PATCH-ACTION=BYVALUE.
                for sameval in set(oldvalues.keys()) & set(newvalues.keys()):
                    newprop = newvalues[sameval].duplicate()
                    newprop.addParameter(Parameter(definitions.cICalParameter_PATCH_ACTION, definitions.cICalParameter_PATCH_ACTION_BYVALUE))
                    patchComponent.addProperty(newprop)

    @staticmethod
    def processSubComponents(oldcomponent, newcomponent, vpatch, path, patchComponent):
        """
        Determine the sub-component differences between two components and create
        appropriate VPATCH entries.

        @param oldcomponent: the old component
        @type oldcomponent: L{Component}
        @param newcomponent: the new component
        @type newcomponent: L{Component}
        @param vpatch: the patch to use
        @type vpatch: L{VPatch}
        @param patchComponent: the PATCH component to add changes to
        @type patchComponent: L{Patch}
        """

        # Use two way set difference to find new and removed (based on the component mapKey)
        oldset = set([component.getMapKey() for component in oldcomponent.getComponents()])
        olduidcount = Counter([component.getUID() for component in oldcomponent.getComponents()])
        oldnamescount = Counter([component.getType() for component in oldcomponent.getComponents()])
        newset = set([component.getMapKey() for component in newcomponent.getComponents()])

        # New ones
        newcompkeys = newset - oldset
        if len(newcompkeys) != 0:
            # Add each component to PATCH
            for newcompkey in newcompkeys:
                newcomp = newcomponent.getComponentByKey(newcompkey)
                patchComponent.addComponent(newcomp.duplicate(parent=patchComponent))

        # Removed ones
        oldcompkeys = oldset - newset
        if len(oldcompkeys) != 0:
            # Add each component to a PATCH-DELETE
            for oldcompkey in oldcompkeys:
                oldcomp = oldcomponent.getComponentByKey(oldcompkey)
                deletepath = "/{}".format(oldcomp.getType())
                # Only add UID= if there was more than one component of this type in the old data and some have different UIDs
                if oldnamescount[oldcomp.getType()] > 1 and oldnamescount[oldcomp.getType()] != olduidcount[oldcomp.getUID()]:
                    deletepath = "{}[UID={}]".format(deletepath, oldcomp.getUID())
                # Only add RID= if there was more than one component with the same UID
                if isinstance(oldcomp, ComponentRecur) and oldnamescount[oldcomp.getType()] > 1 and olduidcount[oldcomp.getUID()] > 1:
                    deletepath = "{}[RID={}]".format(deletepath, str(oldcomp.getRecurrenceID()) if oldcomp.getRecurrenceID() is not None else "M")
                patchComponent.addProperty(Property(definitions.cICalProperty_PATCH_DELETE, deletepath))

        # Ones that exist in both old and new: recurse to have a new PATCH
        # component added for them if they are different
        for compkey in newset & oldset:
            oldcomp = oldcomponent.getComponentByKey(compkey)
            newcomp = newcomponent.getComponentByKey(compkey)
            PatchGenerator.diffComponents(oldcomp, newcomp, vpatch, path)


if __name__ == '__main__':

    import os
    import sys
    olddata = os.path.expanduser(sys.argv[1])
    newdata = os.path.expanduser(sys.argv[2])
    with open(olddata) as f:
        oldcal = Calendar.parseText(f.read())
    with open(newdata) as f:
        newcal = Calendar.parseText(f.read())
    patchcal = PatchGenerator.createPatch(oldcal, newcal)
    print(str(patchcal))
