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
from pycalendar.icalendar import definitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.componentrecur import ComponentRecur
from pycalendar.icalendar.patch import Patch
from pycalendar.icalendar.path import Path
from pycalendar.icalendar.property import Property
from pycalendar.icalendar.vpatch import VPatch
from pycalendar.parameter import Parameter


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
                    parammatch = action.split("@", 1)[1]
                    paramname, paramvalue = parammatch.split("=", 1)
                    oldprops = component.getProperties(newproperty.getName())
                    for oldprop in oldprops:
                        if oldprop.hasParameter(paramname) and paramvalue in oldprop.getParameterValues(paramname):
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
    def getComponentPathSegment(oldcomponent, path, derived):
        """
        Update the path segment to include this component. Decide whether to include
        UID= or RID= match items based on the uniqueness of this component in its
        parent.

        @param oldcomponent: component to process
        @type oldcomponent: L{Component}
        @param path: path to add a segment to
        @type path: L{str}
        @param derived: L{True} if C{oldcomponent} was derived from its master during
            the course of this patch operation
        @type derived: L{bool}
        """

        newpath = "{}/{}".format(path, oldcomponent.getType())
        if oldcomponent.getParentComponent() is None:
            return newpath

        olduid = oldcomponent.getUID()
        oldtype = oldcomponent.getType()
        olduidcount = len([component.getUID() for component in oldcomponent.getParentComponent().getComponents() if component.getUID() == olduid])
        oldnamescount = len([component.getType() for component in oldcomponent.getParentComponent().getComponents() if component.getType() == oldtype])

        # Only add UID= if there was more than one component of this type in the old data and some have different UIDs
        if oldnamescount > 1 and oldnamescount != olduidcount:
            newpath = "{}[UID={}]".format(newpath, oldcomponent.getUID())

        # Only add RID= if there was more than one component with the same UID
        if derived or isinstance(oldcomponent, ComponentRecur) and oldnamescount > 1 and olduidcount > 1:
            newpath = "{}[RID={}]".format(newpath, str(oldcomponent.getRecurrenceID()) if oldcomponent.getRecurrenceID() is not None else "M")

        return newpath

    @staticmethod
    def diffComponents(oldcomponent, newcomponent, vpatch, path, derived=False):
        """
        Recursively traverse the differences between two components, adding
        appropriate items to the VPATCH to describe the differences.

        @param oldcomponent: the old component
        @type oldcomponent: L{Component}
        @param newcomponent: the new component
        @type newcomponent: L{Component}
        @param vpatch: the patch to use
        @type vpatch: L{VPatch}
        @param derived: L{True} if C{oldcomponent} was derived from its master during
            the course of this patch operation
        @type derived: L{bool}
        """

        # Update path to include this component
        path = PatchGenerator.getComponentPathSegment(oldcomponent, path, derived)

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

        # New ones. Add each property to PATCH. Note that if we are adding more
        # than one we need to include PATCH-ACTION=CREATE parameter on each one.
        newpropnames = newset - oldset
        for newpropname in newpropnames:
            actionRequired = len(newcomponent.getProperties(newpropname)) > 1
            for prop in newcomponent.getProperties(newpropname):
                newprop = prop.duplicate()
                if actionRequired:
                    newprop.addParameter(Parameter(definitions.cICalParameter_PATCH_ACTION, definitions.cICalParameter_PATCH_ACTION_CREATE))
                patchComponent.addProperty(newprop)

        # Removed ones. Add each property to a PATCH-DELETE
        oldpropnames = oldset - newset
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
                # Remove ones that are exactly the same
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
        newset = set([component.getMapKey() for component in newcomponent.getComponents()])

        # New ones
        newcompkeys = newset - oldset
        if len(newcompkeys) != 0:
            # Add each component to PATCH
            for newcompkey in newcompkeys:
                newcomp = newcomponent.getComponentByKey(newcompkey)

                # Check to see if we have a recurrence override and special case that
                # as a sub-component diff
                if newcomp.hasProperty(definitions.cICalProperty_RECURRENCE_ID):
                    # Check whether the master exists
                    olduidcomps = oldcomponent.getComponentsByUID(newcomp.getUID())
                    master = [comp for comp in olduidcomps if not comp.hasProperty(definitions.cICalProperty_RECURRENCE_ID)]
                    if len(master) == 1:
                        # Derive an instance from the old master and use that to diff with the new one
                        derived = master[0].deriveComponent(newcomp.getRecurrenceID())
                        PatchGenerator.diffComponents(derived, newcomp, vpatch, path, True)
                        continue

                # Just treat as an entire component add
                patchComponent.addComponent(newcomp.duplicate(parent=patchComponent))

        # Removed ones
        oldcompkeys = oldset - newset
        if len(oldcompkeys) != 0:
            # Add each component to a PATCH-DELETE
            for oldcompkey in oldcompkeys:
                oldcomp = oldcomponent.getComponentByKey(oldcompkey)
                deletepath = PatchGenerator.getComponentPathSegment(oldcomp, "", False)
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
