##
#    Copyright (c) 2007 Cyrus Daboo. All rights reserved.
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

from component import PyCalendarComponent
from vtimezoneelement import PyCalendarVTimezoneElement
import definitions

class PyCalendarVTimezoneStandard(PyCalendarVTimezoneElement):

    sBeginDelimiter = definitions.cICalComponent_BEGINSTANDARD

    sEndDelimiter = definitions.cICalComponent_ENDSTANDARD

    @staticmethod
    def getVBegin():
        return PyCalendarVTimezoneStandard.sBeginDelimiter

    @staticmethod
    def getVEnd():
        return PyCalendarVTimezoneStandard.sEndDelimiter

    def __init__(self, calendar=None, copyit=None):
        if calendar is not None:
            super(PyCalendarVTimezoneStandard, self).__init__(calendar=calendar)
        elif copyit is not None:
            super(PyCalendarVTimezoneStandard, self).__init__(copyit=copyit)

    def clone_it(self):
        return PyCalendarVTimezoneStandard(copyit=self)

    def getType(self):
        return PyCalendarComponent.eVTIMEZONESTANDARD

    def getBeginDelimiter(self):
        return PyCalendarVTimezoneStandard.sBeginDelimiter

    def getEndDelimiter(self):
        return PyCalendarVTimezoneStandard.sEndDelimiter
