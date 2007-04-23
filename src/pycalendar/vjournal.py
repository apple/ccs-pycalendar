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
from componentrecur import PyCalendarComponentRecur
import definitions
import itipdefinitions

class PyCalendarVJournal(PyCalendarComponentRecur):

    sBeginDelimiter = definitions.cICalComponent_BEGINVJOURNAL

    sEndDelimiter = definitions.cICalComponent_ENDVJOURNAL

    @staticmethod
    def getVBegin():
        return PyCalendarVJournal.sBeginDelimiter

    @staticmethod
    def getVEnd():
        return PyCalendarVJournal.sEndDelimiter

    def __init__(self, calendar=None, copyit=None):
        if calendar is not None:
            super(PyCalendarVJournal, self).__init__(calendar=calendar)
        elif copyit is not None:
            super(PyCalendarVJournal, self).__init__(copyit=copyit)

    def clone_it(self):
        return PyCalendarVJournal(copyit=self)

    def getType(self):
        return PyCalendarComponent.eVJOURNAL

    def getBeginDelimiter(self):
        return PyCalendarVJournal.sBeginDelimiter

    def getEndDelimiter(self):
        return PyCalendarVJournal.sEndDelimiter

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VJOURNAL

    def finalise(self):
        super(PyCalendarVJournal, self).finalise()
