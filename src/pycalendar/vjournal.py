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

from componentrecur import PyCalendarComponentRecur
import definitions
import itipdefinitions

class PyCalendarVJournal(PyCalendarComponentRecur):

    def __init__(self, parent=None):
        super(PyCalendarVJournal, self).__init__(parent=parent)

    def duplicate(self, parent=None):
        return super(PyCalendarVJournal, self).duplicate(parent=parent)

    def getType(self):
        return definitions.cICalComponent_VJOURNAL

    def getMimeComponentName(self):
        return itipdefinitions.cICalMIMEComponent_VJOURNAL

    def finalise(self):
        super(PyCalendarVJournal, self).finalise()
