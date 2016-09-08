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
from pycalendar.icalendar.componentrecur import ComponentRecur
from pycalendar.icalendar.path import Path


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
