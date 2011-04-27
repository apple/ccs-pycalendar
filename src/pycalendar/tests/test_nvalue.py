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

from pycalendar.nvalue import NValue
from pycalendar.vcard.property import Property
import unittest

class TestNValue(unittest.TestCase):
    
    def testParseValue(self):
        
        items = (
            ("", ";;;;"),
            (";", ";;;;"),
            (";;;;", ";;;;"),
            ("Cyrus;Daboo;;Dr.", "Cyrus;Daboo;;Dr.;"),
            (";;;;PhD.", ";;;;PhD."),
            ("Cyrus", "Cyrus;;;;"),
            (";Daboo", ";Daboo;;;"),
        )
        
        for item, result in items:
            req = NValue()
            req.parse(item)
            test = req.getText()
            self.assertEqual(test, result, "Failed to parse and re-generate '%s'" % (item,))

    def testParseProperty(self):
        
        items = (
            ("N:", "N:;;;;"),
            ("N:;", "N:;;;;"),
            ("N:;;;;", "N:;;;;"),
            ("N:Cyrus;Daboo;;Dr.", "N:Cyrus;Daboo;;Dr.;"),
            ("N:;;;;PhD.", "N:;;;;PhD."),
            ("N:Cyrus", "N:Cyrus;;;;"),
            ("N:;Daboo", "N:;Daboo;;;"),
            ("N;VALUE=TEXT:Cyrus;Daboo;;Dr.", "N:Cyrus;Daboo;;Dr.;"),
        )
        
        for item, result in items:
            prop = Property()
            prop.parse(item)
            test = prop.getText()
            self.assertEqual(test, result + "\r\n", "Failed to parse and re-generate '%s'" % (item,))
