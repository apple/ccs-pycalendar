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

from pycalendar.adr import Adr
import unittest

class TestAdrValue(unittest.TestCase):
    
    def testInit(self):
        data = (
            (
                ("pobox", "extended", "street", "locality", "region", "postalcode", "country"),
                "pobox;extended;street;locality;region;postalcode;country",
            ),
            (
                (("pobox",), ("extended",), ("street1", "street2",), "locality", "region", (), "country"),
                "pobox;extended;street1,street2;locality;region;;country",
            ),
        )

        for args, result in data:
            a = Adr(*args)
    
            self.assertEqual(
                a.getValue(),
                args,
            )
    
            self.assertEqual(
                a.getText(),
                result,
            )
    
            self.assertEqual(
                a.duplicate().getText(),
                result,
            )
