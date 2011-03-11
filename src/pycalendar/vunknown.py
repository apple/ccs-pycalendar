##
#    Copyright (c) 2011 Cyrus Daboo. All rights reserved.
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
import uuid

class PyCalendarUnknownComponent(PyCalendarComponent):

    def __init__(self, parent=None, comptype=""):
        super(PyCalendarUnknownComponent, self).__init__(parent=parent)
        self.mType = comptype
        self.mMapKey = str(uuid.uuid4())

    def duplicate(self, parent=None):
        return super(PyCalendarUnknownComponent, self).duplicate(parent=parent, comptype=self.mType)

    def getType(self):
        return self.mType

    def getBeginDelimiter(self):
        return "BEGIN:" + self.mType

    def getEndDelimiter(self):
        return "END:" + self.mType

    def getMimeComponentName(self):
        return "unknown"

    def getMapKey(self):
        return self.mMapKey

    def getSortKey(self):
        """
        We do not want unknown components sorted.
        """
        return ""

