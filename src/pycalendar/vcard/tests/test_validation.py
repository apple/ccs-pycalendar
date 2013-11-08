##
#    Copyright (c) 2011-2013 Cyrus Daboo. All rights reserved.
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

from pycalendar.exceptions import ValidationError
from pycalendar.vcard.card import Card
import unittest

class TestValidation(unittest.TestCase):

    def test_basic(self):

        data = (
            (
                "No problems",
                """BEGIN:VCARD
VERSION:3.0
N:Thompson;Default;;;
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "No VERSION",
                """BEGIN:VCARD
VERSION:3.0
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCARD] Missing or too many required property: N",
                )),
            ),
        )

        for title, item, test_fixed, test_unfixed in data:
            card = Card.parseText(item)
            fixed, unfixed = card.validate(doFix=False)
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))


    def test_mode_no_raise(self):

        data = (
            (
                "OK",
                """BEGIN:VCARD
VERSION:3.0
N:Thompson;Default;;;
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
                """BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
FN:Default Thompson
N:Thompson;Default;;;
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Unfixable only",
                """BEGIN:VCARD
VERSION:3.0
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
                """BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
FN:Default Thompson
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCARD] Missing or too many required property: N",
                )),
            ),
        )

        for title, test_old, test_new, test_fixed, test_unfixed in data:
            card = Card.parseText(test_old)
            fixed, unfixed = card.validate(doFix=False, doRaise=False)
            self.assertEqual(str(card), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))


    def test_mode_raise(self):

        data = (
            (
                "OK",
                """BEGIN:VCARD
VERSION:3.0
N:Thompson;Default;;;
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
                """BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
FN:Default Thompson
N:Thompson;Default;;;
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
                set(),
                set(),
                False,
            ),
            (
                "Unfixable only",
                """BEGIN:VCARD
VERSION:3.0
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
                """BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
FN:Default Thompson
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCARD] Missing or too many required property: N",
                )),
                True,
            ),
        )

        for title, test_old, test_new, test_fixed, test_unfixed, test_raises in data:
            card = Card.parseText(test_old)
            if test_raises:
                self.assertRaises(ValidationError, card.validate, doFix=False, doRaise=True)
            else:
                try:
                    fixed, unfixed = card.validate(doFix=False, doRaise=False)
                except:
                    self.fail(msg="Failed test: %s" % (title,))
                self.assertEqual(str(card), test_new, msg="Failed test: %s" % (title,))
                self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
                self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))
