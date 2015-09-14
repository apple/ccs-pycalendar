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

class Vote(Component):

    propertyCardinality_1 = (
    )

    propertyCardinality_0_1 = (
        definitions.cICalProperty_POLL_ITEM_ID,
        definitions.cICalProperty_RESPONSE,
    )

    propertyValueChecks = ICALENDAR_VALUE_CHECKS

    def __init__(self, parent=None):
        super(Vote, self).__init__(parent=parent)


    def duplicate(self, parent=None):
        return super(Vote, self).duplicate(parent=parent)


    def getType(self):
        return definitions.cICalComponent_VOTE


    def sortedPropertyKeyOrder(self):
        return (
            definitions.cICalProperty_POLL_ITEM_ID,
            definitions.cICalProperty_RESPONSE,
        )

Component.registerComponent(definitions.cICalComponent_VOTE, Vote)
