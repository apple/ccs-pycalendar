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

# vCard ADR value

from pycalendar import utils
from pycalendar.valueutils import ValueMixin

class Adr(ValueMixin):
    """
    mValue is a tuple of seven str or tuples of str
    """

    (
        POBOX,
        EXTENDED,
        STREET,
        LOCALITY,
        REGION,
        POSTALCODE,
        COUNTRY,
        MAXITEMS
    ) = range(8)

    def __init__(self, pobox="", extended="", street="", locality="", region="", postalcode="", country=""):
        self.mValue = (pobox, extended, street, locality, region, postalcode, country)


    def duplicate(self):
        return Adr(*self.mValue)


    def __hash__(self):
        return hash(self.mValue)


    def __repr__(self):
        return "ADR %s" % (self.getText(),)


    def __eq__(self, comp):
        return self.mValue == comp.mValue


    def getPobox(self):
        return self.mValue[Adr.POBOX]


    def setPobox(self, value):
        self.mValue[Adr.POBOX] = value


    def getExtended(self):
        return self.mValue[Adr.EXTENDED]


    def setExtended(self, value):
        self.mValue[Adr.EXTENDED] = value


    def getStreet(self):
        return self.mValue[Adr.STREET]


    def setStreet(self, value):
        self.mValue[Adr.STREET] = value


    def getLocality(self):
        return self.mValue[Adr.LOCALITY]


    def setLocality(self, value):
        self.mValue[Adr.LOCALITY] = value


    def getRegion(self):
        return self.mValue[Adr.REGION]


    def setRegion(self, value):
        self.mValue[Adr.REGION] = value


    def getPostalCode(self):
        return self.mValue[Adr.POSTALCODE]


    def setPostalCode(self, value):
        self.mValue[Adr.POSTALCODE] = value


    def getCountry(self):
        return self.mValue[Adr.COUNTRY]


    def setCountry(self, value):
        self.mValue[Adr.COUNTRY] = value


    def parse(self, data):
        self.mValue = utils.parseDoubleNestedList(data, Adr.MAXITEMS)


    def generate(self, os):
        utils.generateDoubleNestedList(os, self.mValue)


    def getValue(self):
        return self.mValue


    def setValue(self, value):
        self.mValue = value
