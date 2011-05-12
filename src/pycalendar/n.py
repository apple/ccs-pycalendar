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

# vCard ADR value

from pycalendar import utils
from pycalendar.valueutils import ValueMixin

class N(ValueMixin):
    """
    mValue is a tuple of seven str or tuples of str
    """

    # This is the order of fields in the vCard property value
    (
        LAST,
        FIRST,
        MIDDLE,
        PREFIX,
        SUFFIX,
        MAXITEMS
    ) = range(6)

    def __init__(self, last="", first="", middle="", prefix="", suffix=""):
        self.mValue = (last, first, middle, prefix, suffix)

    def duplicate(self):
        return N(*self.mValue)

    def __hash__(self):
        return hash(self.mValue)

    def __repr__(self):
        return "N %s" % (self.getText(),)

    def __eq__( self, comp ):
        return self.mValue == comp.mValue

    def getFirst(self):
        return self.mValue[N.FIRST]
    
    def setFirst(self, value):
        self.mValue[N.FIRST] = value

    def getLast(self):
        return self.mValue[N.LAST]
    
    def setLast(self, value):
        self.mValue[N.LAST] = value

    def getMiddle(self):
        return self.mValue[N.MIDDLE]
    
    def setMiddle(self, value):
        self.mValue[N.MIDDLE] = value

    def getPrefix(self):
        return self.mValue[N.PREFIX]
    
    def setPrefix(self, value):
        self.mValue[N.PREFIX] = value

    def getSuffix(self):
        return self.mValue[N.SUFFIX]
    
    def setSuffix(self, value):
        self.mValue[N.SUFFIX] = value

    def getFullName(self):
        
        def _stringOrList(item):
            return item if isinstance(item, basestring) else " ".join(item)

        results = []
        for i in (N.PREFIX, N.FIRST, N.MIDDLE, N.LAST, N.SUFFIX):
            result = _stringOrList(self.mValue[i])
            if result:
                results.append(result)

        return " ".join(results)

    def parse(self, data):
        self.mValue = utils.parseDoubleNestedList(data, N.MAXITEMS)

    def generate(self, os):
        utils.generateDoubleNestedList(os, self.mValue)

    def getValue(self):
        return self.mValue

    def setValue(self, value):
        self.mValue = value
