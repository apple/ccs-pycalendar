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

from pycalendar.icalendar import definitions
from pycalendar.icalendar.component import Component
from pycalendar.icalendar.vtimezoneelement import VTimezoneElement

class Standard(VTimezoneElement):

    def __init__(self, parent=None):
        super(Standard, self).__init__(parent=parent)


    def duplicate(self, parent=None):
        return super(Standard, self).duplicate(parent=parent)


    def getType(self):
        return definitions.cICalComponent_STANDARD

Component.registerComponent(definitions.cICalComponent_STANDARD, Standard)
