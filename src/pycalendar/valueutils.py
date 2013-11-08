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

# Helpers for value classes

from cStringIO import StringIO

class ValueMixin(object):
    """
    Mix-in for operations common to Value's and value-specific classes.
    """

    def __str__(self):
        return self.getText()


    @classmethod
    def parseText(cls, data):
        value = cls()
        value.parse(data)
        return value


    def parse(self, data):
        raise NotImplementedError


    def generate(self, os):
        raise NotImplementedError


    def getText(self):
        os = StringIO()
        self.generate(os)
        return os.getvalue()


    def writeXML(self, node, namespace):
        raise NotImplementedError


    def parseJSON(self, jobject):
        raise NotImplementedError


    def writeJSON(self, jobject):
        raise NotImplementedError



class WrapperValue(object):
    """
    Mix-in for Value derived classes that wrap a value-specific class.
    """

    _wrappedClass = None
    _wrappedType = None

    def __init__(self, value=None):
        self.mValue = value if value is not None else self._wrappedClass()


    def getType(self):
        return self._wrappedType


    def duplicate(self):
        return self.__class__(self.mValue.duplicate())


    def parse(self, data, variant):
        self.mValue.parse(data)


    def generate(self, os):
        self.mValue.generate(os)


    def writeXML(self, node, namespace):
        value = self.getXMLNode(node, namespace)
        value.text = self.mValue.writeXML()


    def parseJSONValue(self, jobject):
        self.mValue.parseJSON(jobject)


    def writeJSONValue(self, jobject):
        self.mValue.writeJSON(jobject)


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value
