##
#    Copyright (c) 2007-2012 Cyrus Daboo. All rights reserved.
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

from pycalendar import definitions
from vtimezoneelement import PyCalendarVTimezoneElement

class PyCalendarVTimezoneDaylight(PyCalendarVTimezoneElement):

    def __init__(self, parent=None):
        super(PyCalendarVTimezoneDaylight, self).__init__(parent=parent)


    def duplicate(self, parent=None):
        return super(PyCalendarVTimezoneDaylight, self).duplicate(parent=parent)


    def getType(self):
        return definitions.cICalComponent_DAYLIGHT
