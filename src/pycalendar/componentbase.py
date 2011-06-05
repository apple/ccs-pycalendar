##
#    Copyright (c) 2007-2011 Cyrus Daboo. All rights reserved.
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
from pycalendar import xmldefs
from pycalendar.datetimevalue import PyCalendarDateTimeValue
from pycalendar.periodvalue import PyCalendarPeriodValue
from pycalendar.property import PyCalendarProperty
from pycalendar.value import PyCalendarValue
import xml.etree.cElementTree as XML

class PyCalendarComponentBase(object):

    def __init__(self, parent=None):
        self.mParentComponent = parent
        self.mComponents = []
        self.mProperties = {}

    def duplicate(self, **args):
        other = self.__class__(**args)
        
        for component in self.mComponents:
            other.addComponent(component.duplicate(parent=other))

        other.mProperties = {}
        for propname, props in self.mProperties.iteritems():
            other.mProperties[propname] = [i.duplicate() for i in props]
        return other
    
    def __str__(self):
        return self.getText()

    def __ne__(self, other): return not self.__eq__(other)
    def __eq__(self, other):
        if not isinstance(other, PyCalendarComponentBase): return False
        return self.getType() == other.getType() and self.compareProperties(other) and self.compareComponents(other)

    def getType(self):
        raise NotImplementedError

    def getBeginDelimiter(self):
        return "BEGIN:" + self.getType()

    def getEndDelimiter(self):
        return "END:" + self.getType()

    def getSortKey(self):
        return ""

    def getParentComponent(self):
        return self.mParentComponent
    
    def setParentComponent(self, parent):
        self.mParentComponent = parent

    def compareComponents(self, other):
        mine = set(self.mComponents)
        theirs = set(other.mComponents)
        
        for item in mine:
            for another in theirs:
                if item == another:
                    theirs.remove(another)
                    break
            else:
                return False
        return len(theirs) == 0

    def getComponents(self, compname=None):
        compname = compname.upper() if compname else None
        return [component for component in self.mComponents if compname is None or component.getType().upper() == compname]
        
    def getComponentByKey(self, key):
        for component in self.mComponents:
            if component.getMapKey() == key:
                return component
        else:
            return None
        
    def removeComponentByKey(self, key):

        for component in self.mComponents:
            if component.getMapKey() == key:
                self.removeComponent(component)
                return

    def addComponent(self, component):
        self.mComponents.append(component)

    def hasComponent(self, compname):
        return self.countComponents(compname) != 0

    def countComponents(self, compname):
        return len(self.getComponents(compname))

    def removeComponent(self, component):
        self.mComponents.remove(component)

    def removeAllComponent(self, compname=None):
        if compname:
            compname = compname.upper()
            for component in tuple(self.mComponents):
                if component.getType().upper() == compname:
                    self.removeComponent(component)
        else:
            self.mComponents = []

    def sortedComponentNames(self):
        return ()

    def compareProperties(self, other):
        mine = set()
        for props in self.mProperties.values():
            mine.update(props)
        theirs = set()
        for props in other.mProperties.values():
            theirs.update(props)
        return mine == theirs

    def getProperties(self, propname=None):
        return self.mProperties.get(propname.upper(), []) if propname else self.mProperties

    def setProperties(self, props):
        self.mProperties = props

    def addProperty(self, prop):
        self.mProperties.setdefault(prop.getName().upper(), []).append(prop)

    def hasProperty(self, propname):
        return self.mProperties.has_key(propname.upper())

    def countProperty(self, propname):
        return len(self.mProperties.get(propname.upper(), []))

    def findFirstProperty(self, propname):
        return self.mProperties.get(propname.upper(), [None])[0]

    def removeProperty(self, prop):
        if self.mProperties.has_key(prop.getName().upper()):
            self.mProperties[prop.getName().upper()].remove(prop)
            if len(self.mProperties[prop.getName().upper()]) == 0:
                del self.mProperties[prop.getName().upper()]

    def removeProperties(self, propname):
        if self.mProperties.has_key(propname.upper()):
            del self.mProperties[propname.upper()]

    def getPropertyInteger(self, prop, type = None):
        return self.loadValueInteger(prop, type)

    def getPropertyString(self, prop):
        return self.loadValueString(prop)

    def getProperty(self, prop, value):
        return self.loadValue(prop, value)

    def finalise(self):
        raise NotImplemented

    def getText(self):
        s = StringIO()
        self.generate(s)
        return s.getvalue()

    def generate(self, os):
        # Header
        os.write(self.getBeginDelimiter())
        os.write("\r\n")

        # Write each property
        self.writeProperties(os)

        # Write each embedded component based on specific order
        self.writeComponents(os)

        # Footer
        os.write(self.getEndDelimiter())
        os.write("\r\n")

    def generateFiltered(self, os, filter):
        # Header
        os.write(self.getBeginDelimiter())
        os.write("\r\n")

        # Write each property
        self.writePropertiesFiltered(os, filter)

        # Write each embedded component based on specific order
        self.writeComponentsFiltered(os, filter)

        # Footer
        os.write(self.getEndDelimiter())
        os.write("\r\n")

    def writeXML(self, node, namespace):
        
        # Component element
        comp = XML.SubElement(node, xmldefs.makeTag(namespace, self.getType()))
        
        # Each property
        self.writePropertiesXML(comp, namespace)
    
        # Each component
        self.writeComponentsXML(comp, namespace)
    
    def writeXMLFiltered(self, node, namespace, filter):
        # Component element
        comp = XML.SubElement(node, xmldefs.makeTag(namespace, self.getType()))
        
        # Each property
        self.writePropertiesFilteredXML(comp, namespace, filter)
    
        # Each component
        self.writeComponentsFilteredXML(comp, namespace, filter)

    def sortedComponents(self):
        
        components = self.mComponents[:]
        sortedcomponents = []

        # Write each component based on specific order
        orderedNames = self.sortedComponentNames()
        for name in orderedNames:
            
            # Group by name then sort by map key (UID/R-ID)
            namedcomponents = []
            for component in tuple(components):
                if component.getType().upper() == name:
                    namedcomponents.append(component)
                    components.remove(component)
            for component in sorted(namedcomponents, key=lambda x:x.getSortKey()):
                sortedcomponents.append(component)
        
        # Write out the remainder 
        for component in components:
            sortedcomponents.append(component)
            
        return sortedcomponents
        
    def writeComponents(self, os):
        
        # Write out the remainder 
        for component in self.sortedComponents():
            component.generate(os)
        
    def writeComponentsFiltered(self, os, filter):
        # Shortcut for all sub-components
        if filter.isAllSubComponents():
            self.writeComponents(os)
        elif filter.hasSubComponentFilters():
            for subcomp in self.sortedcomponents():
                subfilter = filter.getSubComponentFilter(subcomp.getType())
                if subfilter is not None:
                    subcomp.generateFiltered(os, subfilter)
        
    def writeComponentsXML(self, node, namespace):
        
        if self.mComponents:
            comps = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.components))
            
            # Write out the remainder 
            for component in self.sortedComponents():
                component.writeXML(comps, namespace)
        
    def writeComponentsFilteredXML(self, node, namespace, filter):

        if self.mComponents:
            comps = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.components))
            
            # Shortcut for all sub-components
            if filter.isAllSubComponents():
                self.writeXML(comps, namespace)
            elif filter.hasSubComponentFilters():
                for subcomp in self.sortedcomponents():
                    subfilter = filter.getSubComponentFilter(subcomp.getType())
                    if subfilter is not None:
                        subcomp.writeFilteredXML(comps, namespace, subfilter)
        
    def loadValue(self, value_name):
        if self.hasProperty(value_name):
            return self.findFirstProperty(value_name)

        return None

    def loadValueInteger(self, value_name, type=None):
        if type:
            if self.hasProperty(value_name):
                if type == PyCalendarValue.VALUETYPE_INTEGER:
                    ivalue = self.findFirstProperty(value_name).getIntegerValue()
                    if ivalue is not None:
                        return ivalue.getValue()
                elif type == PyCalendarValue.VALUETYPE_UTC_OFFSET:
                    uvalue = self.findFirstProperty(value_name).getUTCOffsetValue()
                    if (uvalue is not None):
                        return uvalue.getValue()
    
            return None
        else:
            return self.loadValueInteger(value_name, PyCalendarValue.VALUETYPE_INTEGER)

    def loadValueString(self, value_name):
        if self.hasProperty(value_name):
            tvalue = self.findFirstProperty(value_name).getTextValue()
            if (tvalue is not None):
                return tvalue.getValue()

        return None

    def loadValueDateTime(self, value_name):
        if self.hasProperty(value_name):
            dtvalue = self.findFirstProperty(value_name).getDateTimeValue()
            if dtvalue is not None:
                return dtvalue.getValue()

        return None

    def loadValueDuration(self, value_name):
        if self.hasProperty(value_name):
            dvalue = self.findFirstProperty(value_name).getDurationValue()
            if (dvalue is not None):
                return dvalue.getValue()

        return None

    def loadValuePeriod(self, value_name):
        if self.hasProperty(value_name):
            pvalue = self.findFirstProperty(value_name).getPeriodValue()
            if (pvalue is not None):
                return pvalue.getValue()

        return None

    def loadValueRRULE(self, value_name, value, add):
        # Get RRULEs
        if self.hasProperty(value_name):
            items = self.getProperties()[value_name]
            for iter in items:
                rvalue = iter.getRecurrenceValue()
                if (rvalue is not None):
                    if add:
                        value.addRule(rvalue.getValue())
                    else:
                        value.subtractRule(rvalue.getValue())
            return True
        else:
            return False

    def loadValueRDATE(self, value_name, value, add):
        # Get RDATEs
        if self.hasProperty(value_name):
            for iter in self.getProperties(value_name):
                mvalue = iter.getMultiValue()
                if (mvalue is not None):
                    for obj in mvalue.getValues():
                        # cast to date-time
                        if isinstance(obj, PyCalendarDateTimeValue):
                            if add:
                                value.addDT(obj.getValue())
                            else:
                                value.subtractDT(obj.getValue())
                        elif isinstance(obj, PyCalendarPeriodValue):
                            if add:
                                value.addPeriod(obj.getValue().getStart())
                            else:
                                value.subtractPeriod(obj.getValue().getStart())

            return True
        else:
            return False

    def sortedPropertyKeys(self):
        keys = self.mProperties.keys()
        keys.sort()
        
        results = []
        for skey in self.sortedPropertyKeyOrder():
            if skey in keys:
                results.append(skey)
                keys.remove(skey)
        results.extend(keys)
        return results

    def sortedPropertyKeyOrder(self):
        return ()

    def writeProperties(self, os):
        # Sort properties by name
        keys = self.sortedPropertyKeys()
        for key in keys:
            props = self.mProperties[key]
            for prop in props:
                prop.generate(os)

    def writePropertiesFiltered(self, os, filter):

        # Sort properties by name
        keys = self.sortedPropertyKeys()

        # Shortcut for all properties
        if filter.isAllProperties():
            for key in keys:
                for prop in self.getProperties(key):
                    prop.generate(os)
        elif filter.hasPropertyFilters():
            for key in keys:
                for prop in self.getProperties(key):
                    prop.generateFiltered(os, filter)

    def writePropertiesXML(self, node, namespace):

        properties = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.properties))
        
        # Sort properties by name
        keys = self.sortedPropertyKeys()
        for key in keys:
            props = self.mProperties[key]
            for prop in props:
                prop.writeXML(properties, namespace)

    def writePropertiesFilteredXML(self, node, namespace, filter):

        props = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.properties))
        
        # Sort properties by name
        keys = self.sortedPropertyKeys()

        # Shortcut for all properties
        if filter.isAllProperties():
            for key in keys:
                for prop in self.getProperties(key):
                    prop.writeXML(props, namespace)
        elif filter.hasPropertyFilters():
            for key in keys:
                for prop in self.getProperties(key):
                    prop.writeFilteredXML(props, namespace, filter)

    def loadPrivateValue(self, value_name):
        # Read it in from properties list and then delete the property from the
        # main list
        result = self.loadValueString(value_name)
        if (result is not None):
            self.removeProperties(value_name)
        return result

    def writePrivateProperty(self, os, key, value):
        prop = PyCalendarProperty(name=key, value=value)
        prop.generate(os)

    def editProperty(self, propname, propvalue):

        # Remove existing items
        self.removeProperties(propname)

        # Now create properties
        if propvalue:
            self.addProperty(PyCalendarProperty(name=propname, value=propvalue))
