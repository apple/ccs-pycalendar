##
#    Copyright (c) 2011-2015 Cyrus Daboo. All rights reserved.
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
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.validation import ICALENDAR_VALUE_CHECKS

class VVoter(Component):

    propertyCardinality_1 = (
        definitions.cICalProperty_VOTER,
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_CREATED,
        definitions.cICalProperty_DESCRIPTION,
        definitions.cICalProperty_LAST_MODIFIED,
        definitions.cICalProperty_SUMMARY,
        definitions.cICalProperty_URL,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):
        super(VVoter, self).__init__(parent=parent)


    def duplicate(self, parent=None):
        return super(VVoter, self).duplicate(parent=parent)


    def getType(self):
        return definitions.cICalComponent_VVOTER


    def addComponent(self, comp):
        # We can embed the available components only
        if comp.getType() == definitions.cICalComponent_VOTE:
            super(VVoter, self).addComponent(comp)
        else:
            raise ValueError


    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_VOTER,
        )


    def sortedComponents(self):
        """
        Also take POLL-ITEM-ID into account
        """

        components = self.mComponents[:]
        return sorted(components, key=lambda x: x.loadValueInteger(definitions.cICalProperty_POLL_ITEM_ID))

Component.registerComponent(definitions.cICalComponent_VVOTER, VVoter)
