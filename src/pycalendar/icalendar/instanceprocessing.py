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

from pycalendar.icalendar import definitions
from pycalendar.icalendar.calendar import Calendar
from pycalendar.icalendar.componentrecur import ComponentRecur
from pycalendar.icalendar.path import Path
from pycalendar.icalendar.property import Property
from pycalendar.icalendar.vinstance import VInstance
from pycalendar.parameter import Parameter


class InstanceExpander(object):
    """
    Expand an iCalendar object with VINSTANCE components into the full set of
    overridden components.
    """

    @staticmethod
    def expand(calendar):
        """
        Expand VINSTANCEs in the supplied iCalendar object. This mutates the supplied
        L{Calendar} into the result.

        @param calendar: the calendar to expand
        @type calendar: L{Calendar}
        """

        # Apply expansion to all master components that are immediate children
        # of the calendar component
        for component in calendar.getComponents():
            if isinstance(component, ComponentRecur) and component.isRecurring() and component.isMasterInstance():
                InstanceExpander.expandComponent(component)

    @staticmethod
    def expandComponent(component):
        """
        Expand VINSTANCEs in the supplied iCalendar component. This mutates the supplied
        L{Component} and its parent as the result.

        @param component: the calendar to expand
        @type component: L{ComponentRecur}
        """

        # First remember and remove all VINSTANCEs from the master so that we don't
        # end up including them in derived instances
        vinstances = tuple(component.getComponents(definitions.cICalComponent_VINSTANCE))
        component.removeAllComponent(definitions.cICalComponent_VINSTANCE)

        # Process each VINSTANCE
        for instance in vinstances:
            InstanceExpander.expandInstance(component, instance)

    @staticmethod
    def expandInstance(master, instance):
        """
        Expand the supplied VINSTANCE in the supplied iCalendar component. This mutates the supplied
        L{Component} and its parent as the result.

        @param master: the master component
        @type master: L{ComponentRecur}
        @param instance: the VINSTANCE to expand
        @type instance: L{VInstance}
        """

        # Generate the derived instance first, then apply VINSTANCE changes to it
        derived = master.deriveComponent(instance.getRecurrenceID())
        master.getParentComponent().addComponent(derived)

        # Process deletes first
        for prop in instance.getProperties(definitions.cICalProperty_INSTANCE_DELETE):
            path = Path(prop.getTextValue().getValue())
            InstanceExpander.processDelete(path, derived)

        # Process components, then properties
        InstanceExpander.processSubComponents(instance, derived)
        InstanceExpander.processProperties(instance, derived)

    @staticmethod
    def processDelete(path, derived):
        """
        Execute a delete action on the matched items.

        @param path: path being processed
        @type path: L{Path}
        @param derived: component to update
        @type derived: L{Component}
        """

        matches = path.match(derived)

        if path.targetComponent():
            for component in matches:
                component.removeFromParent()

        elif path.targetProperty():
            for component, property in matches:
                component.removeProperty(property)

        else:
            raise ValueError("delete path is not valid: {}".format(path))

    @staticmethod
    def processSubComponents(instance, derived):
        """
        Process component add/replace from VINSTANCE in the derived instance.

        @param instance: the VINSTANCE to expand
        @type instance: L{VInstance}
        @param derived: component to update
        @type derived: L{Component}
        """
        for newcomponent in instance.getComponents():
            mapkey = newcomponent.getMapKey()
            derived.removeComponentByKey(mapkey)
            derived.addComponent(newcomponent.duplicate(parent=derived))

    @staticmethod
    def processProperties(instance, derived):
        """
        Process property add/replace from VINSTANCE in the derived instance.

        @param instance: the VINSTANCE to expand
        @type instance: L{VInstance}
        @param derived: component to update
        @type derived: L{Component}
        """
        for propname, newpropertylist in instance.getProperties().items():
            if propname == definitions.cICalProperty_INSTANCE_DELETE:
                continue
            for newproperty in newpropertylist:
                if newproperty.hasParameter(definitions.cICalParameter_INSTANCE_ACTION):
                    action = newproperty.getParameterValue(definitions.cICalParameter_INSTANCE_ACTION)
                    newproperty.removeParameters(definitions.cICalParameter_INSTANCE_ACTION)
                else:
                    action = None

                # Always replace
                if action is None:
                    derived.removeProperties(newproperty.getName())
                    derived.addProperty(newproperty.duplicate())

                # Just add
                elif action == definitions.cICalParameter_INSTANCE_ACTION_CREATE:
                    derived.addProperty(newproperty.duplicate())

                # Replace property with the same value
                elif action == definitions.cICalParameter_INSTANCE_ACTION_BYVALUE:
                    oldprops = derived.getProperties(newproperty.getName())
                    newvalue = newproperty.getValue()
                    for oldprop in oldprops:
                        if oldprop.getValue() == newvalue:
                            derived.removeProperty(oldprop)
                    derived.addProperty(newproperty.duplicate())

                # Replace property with the same param value
                elif action.startswith(definitions.cICalParameter_INSTANCE_ACTION_BYPARAM):
                    parammatch = action.split("@", 1)[1]
                    paramname, paramvalue = parammatch.split("=", 1)
                    oldprops = derived.getProperties(newproperty.getName())
                    for oldprop in oldprops:
                        if oldprop.hasParameter(paramname) and paramvalue in oldprop.getParameterValues(paramname):
                            derived.removeProperty(oldprop)
                    derived.addProperty(newproperty.duplicate())

                # Invalid parameter value
                else:
                    raise ValueError("INSTANCE-ACTION value is not valid: {}".format(action))


class InstanceCompactor(object):
    """
    Class that converts a traditional overridden component representation to the
    new more compact VINSTANCE style.
    """

    @staticmethod
    def compact(calendar):
        """
        Turn overridden components into VINSTANCEs. This mutates the supplied
        L{Calendar} into the result.

        @param calendar: the calendar to compact
        @type calendar: L{Calendar}
        """

        # Process sets of components by UID
        byuid = {}
        for component in calendar.getComponents():
            if isinstance(component, ComponentRecur):
                uid = component.getUID()
                rid = component.getRecurrenceID()
                if uid not in byuid:
                    byuid[uid] = [None, []]
                if rid is None:
                    byuid[uid][0] = component
                else:
                    byuid[uid][1].append(component)

        vinstances = []
        for uid, items in byuid.items():
            master, overrides = items
            for override in overrides:
                vinstances.append(InstanceCompactor.processMasterOverride(master, override))

        for vinstance in vinstances:
            master.addComponent(vinstance)

    @staticmethod
    def processMasterOverride(master, override):
        """
        Compact the override into the master as a VINSTANCE component.

        @param master: master component
        @type master: L{ComponentRecur}
        @param override: override to compact
        @type override: L{ComponentRecur}
        """

        # Need to diff the derived instance with the override
        derived = master.deriveComponent(override.getRecurrenceID())
        vinstance = VInstance(parent=master)
        vinstance.addProperty(override.findFirstProperty(definitions.cICalProperty_RECURRENCE_ID).duplicate())

        # Process properties then sub-components
        InstanceCompactor.processProperties(derived, override, vinstance)
        InstanceCompactor.processSubComponents(derived, override, vinstance)

        # Remove/add components
        override.getParentComponent().removeComponent(override)
        return vinstance

    @staticmethod
    def processProperties(derived, override, vinstance):
        """
        Determine the property differences between two components and create
        appropriate VINSTANCE entries.

        @param derived: the derived component
        @type derived: L{Component}
        @param override: the overridden component
        @type override: L{Component}
        @param vinstance: the vinstance to update
        @type vinstance: L{VInstance}
        """

        # Use two way set difference to find new and removed
        oldset = set(derived.getProperties().keys())
        newset = set(override.getProperties().keys())

        # New ones. Add each property to VINSTANCE. Note that if we are adding more
        # than one we need to include INSTANCE-ACTION=CREATE parameter on each one.
        newpropnames = newset - oldset
        for newpropname in newpropnames:
            actionRequired = len(override.getProperties(newpropname)) > 1
            for prop in override.getProperties(newpropname):
                newprop = prop.duplicate()
                if actionRequired:
                    newprop.addParameter(Parameter(definitions.cICalParameter_INSTANCE_ACTION, definitions.cICalParameter_INSTANCE_ACTION_CREATE))
                vinstance.addProperty(newprop)

        # Removed ones. Add each property to a INSTANCE-DELETE
        oldpropnames = oldset - newset
        for oldpropname in oldpropnames:
            vinstance.addProperty(Property(definitions.cICalProperty_INSTANCE_DELETE, "#{}".format(oldpropname)))

        # Ones that exist in both old and new: this is tricky as we now need to find out what is different.
        # We handle two cases: single occurring properties vs multi-occurring
        checkpropnames = newset & oldset
        for propname in checkpropnames:
            oldprops = derived.getProperties(propname)
            newprops = override.getProperties(propname)

            # Look for singletons
            if len(oldprops) == 1 and len(newprops) == 1:
                # Check for difference
                if oldprops[0] != newprops[0]:
                    vinstance.addProperty(newprops[0].duplicate())

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
                    vinstance.addProperty(Property(definitions.cICalProperty_INSTANCE_DELETE, "#{}[={}]".format(propname, removeval)))

                # Ones to create (ones whose value only exists in the new set). Add as INSTANCE-ACTION=CREATE.
                for createval in set(newvalues.keys()) - set(oldvalues.keys()):
                    newprop = newvalues[createval].duplicate()
                    newprop.addParameter(Parameter(definitions.cICalParameter_INSTANCE_ACTION, definitions.cICalParameter_INSTANCE_ACTION_CREATE))
                    vinstance.addProperty(newprop)

                # Ones with the same value - check if parameters are different. Add as INSTANCE-ACTION=BYVALUE.
                for sameval in set(oldvalues.keys()) & set(newvalues.keys()):
                    newprop = newvalues[sameval].duplicate()
                    newprop.addParameter(Parameter(definitions.cICalParameter_INSTANCE_ACTION, definitions.cICalParameter_INSTANCE_ACTION_BYVALUE))
                    vinstance.addProperty(newprop)

    @staticmethod
    def processSubComponents(derived, override, vinstance):
        """
        Determine the sub-component differences between two components and create
        appropriate VINSTANCE entries.

        @param derived: the derived component
        @type derived: L{Component}
        @param override: the overridden component
        @type override: L{Component}
        @param vinstance: the vinstance to update
        @type vinstance: L{VInstance}
        """

        # Use two way set difference to find new and removed (based on the component mapKey)
        oldset = set([component.getMapKey() for component in derived.getComponents()])
        newset = set([component.getMapKey() for component in override.getComponents()])

        # New ones
        newcompkeys = newset - oldset
        if len(newcompkeys) != 0:
            # Add each component to VINSTANCE
            for newcompkey in newcompkeys:
                newcomp = override.getComponentByKey(newcompkey)
                vinstance.addComponent(newcomp.duplicate(parent=vinstance))

        # Removed ones
        oldcompkeys = oldset - newset
        if len(oldcompkeys) != 0:
            # Add each component to an INSTANCE-DELETE
            for oldcompkey in oldcompkeys:
                oldcomp = derived.getComponentByKey(oldcompkey)
                deletepath = "/{}[UID={}]".format(oldcomp.getType(), oldcomp.getUID())
                vinstance.addProperty(Property(definitions.cICalProperty_INSTANCE_DELETE, deletepath))

        # Ones that exist in both old and new: add to VINSTANCE if different
        for compkey in newset & oldset:
            oldcomp = derived.getComponentByKey(compkey)
            newcomp = override.getComponentByKey(compkey)
            if oldcomp != newcomp:
                vinstance.addComponent(newcomp.duplicate(parent=vinstance))


if __name__ == '__main__':

    import os
    olddata = os.path.expanduser("~/Desktop/overridden.ics")  # sys.argv[1])
    with open(olddata) as f:
        oldcal = Calendar.parseText(f.read())
    InstanceCompactor.compact(oldcal)
    print(str(oldcal))
