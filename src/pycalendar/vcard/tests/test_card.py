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

from pycalendar.exceptions import InvalidData
from pycalendar.parser import ParserContext
from pycalendar.vcard.card import Card
from pycalendar.vcard.property import Property
import cStringIO as StringIO
import difflib
import unittest

class TestCard(unittest.TestCase):

    data = (
        (
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
        ),
        (
"""BEGIN:VCARD
VERSION:3.0
N:Thompson;Default;;;
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
BDAY:2001-01-02
REV:2011-01-02T12:34:56-0500
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
"""BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
BDAY:20010102
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
FN:Default Thompson
N:Thompson;Default;;;
REV:20110102T123456-0500
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
        ),
        (
"""BEGIN:VCARD
VERSION:3.0
N:Thompson;Default;;;
FN:Default Thompson
EMAIL;type=INTERNET;WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
BDAY:2001-01-02
REV:2011-01-02T12:34:56-0500
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
"""BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
BDAY:20010102
EMAIL;type=INTERNET;type=pref;WORK:lthompson@example.com
FN:Default Thompson
N:Thompson;Default;;;
REV:20110102T123456-0500
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
        ),
        (
"""BEGIN:VCARD
VERSION:3.0
N:Picture;With;;;
FN:With Picture
EMAIL;type=INTERNET;type=WORK;type=pref:withpicture@example.com
TEL;type=WORK;type=pref:777-777-7777
TEL;type=CELL:8888888888
item1.ADR;type=WORK;type=pref:;;1234 Golly Street;Sunnyside;CA;99999;USA
item1.X-ABADR:us
PHOTO;Encoding=b:QkVHSU46VkNBUkQKVkVSU0lPTjozLjAKTjpQaWN0dXJlO1dpdGg7Ozs
 KRk46V2l0aCBQaWN0dXJlCkVNQUlMO3R5cGU9SU5URVJORVQ7dHlwZT1XT1JLO3R5cGU9cH
 JlZjp3aXRocGljdHVyZUBleGFtcGxlLmNvbQpURUw7dHlwZT1XT1JLO3R5cGU9cHJlZjo3N
 zctNzc3LTc3NzcKVEVMO3R5cGU9Q0VMTDo4ODg4ODg4ODg4Cml0ZW0xLkFEUjt0eXBlPVdP
 Uks7dHlwZT1wcmVmOjs7MTIzNCBHb2xseSBTdHJlZXQ7U3VubnlzaWRlO0NBOzk5OTk5O1V
 TQQppdGVtMS5YLUFCQURSOnVzClBIT1RPO0JBU0U2NDoKVUlEOjkzNDczMUM2LTFDOTUtNE
 M0MC1CRTFGLUZBNDIxNUIyMzA3QjpBQlBlcnNvbgpFTkQ6VkNBUkQK
UID:934731C6-1C95-4C40-BE1F-FA4215B2307B:ABPerson
END:VCARD
""".replace("\n", "\r\n"),
"""BEGIN:VCARD
VERSION:3.0
UID:934731C6-1C95-4C40-BE1F-FA4215B2307B:ABPerson
item1.ADR;type=WORK;type=pref:;;1234 Golly Street;Sunnyside;CA;99999;USA
EMAIL;type=INTERNET;type=WORK;type=pref:withpicture@example.com
FN:With Picture
N:Picture;With;;;
PHOTO;Encoding=b:
 QkVHSU46VkNBUkQKVkVSU0lPTjozLjAKTjpQaWN0dXJlO1dpdGg7OzsKRk46V2l0aCBQaWN0
 dXJlCkVNQUlMO3R5cGU9SU5URVJORVQ7dHlwZT1XT1JLO3R5cGU9cHJlZjp3aXRocGljdHVy
 ZUBleGFtcGxlLmNvbQpURUw7dHlwZT1XT1JLO3R5cGU9cHJlZjo3NzctNzc3LTc3NzcKVEVM
 O3R5cGU9Q0VMTDo4ODg4ODg4ODg4Cml0ZW0xLkFEUjt0eXBlPVdPUks7dHlwZT1wcmVmOjs7
 MTIzNCBHb2xseSBTdHJlZXQ7U3VubnlzaWRlO0NBOzk5OTk5O1VTQQppdGVtMS5YLUFCQURS
 OnVzClBIT1RPO0JBU0U2NDoKVUlEOjkzNDczMUM2LTFDOTUtNEM0MC1CRTFGLUZBNDIxNUIy
 MzA3QjpBQlBlcnNvbgpFTkQ6VkNBUkQK
TEL;type=WORK;type=pref:777-777-7777
TEL;type=CELL:8888888888
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
        ),
        (
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
X-APPLE-STRUCTURED-LOCATION;VALUE=URI:geo:123.123,123.123
X-Test:Some\, text.
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
X-APPLE-STRUCTURED-LOCATION;VALUE=URI:geo:123.123,123.123
X-Test:Some\, text.
END:VCARD
""".replace("\n", "\r\n"),
        ),
    )


    def testRoundtrip(self):


        def _doRoundtrip(caldata, resultdata=None):
            test1 = resultdata if resultdata is not None else caldata

            card = Card()
            card.parse(StringIO.StringIO(caldata))

            s = StringIO.StringIO()
            card.generate(s)
            test2 = s.getvalue()

            self.assertEqual(
                test1,
                test2,
                "\n".join(difflib.unified_diff(test1.splitlines(), test2.splitlines())),
            )

        for item, result in self.data:
            _doRoundtrip(item, result)


    def testRoundtripDuplicate(self):


        def _doDuplicateRoundtrip(caldata, result):
            card = Card()
            card.parse(StringIO.StringIO(caldata))
            card = card.duplicate()

            s = StringIO.StringIO()
            card.generate(s)
            test = s.getvalue()
            self.assertEqual(test, result, "\n".join(difflib.unified_diff(test.splitlines(), result.splitlines())))

        for item, result in self.data:
            _doDuplicateRoundtrip(item, result)


    def testEquality(self):


        def _doEquality(caldata):
            card1 = Card()
            card1.parse(StringIO.StringIO(caldata))

            card2 = Card()
            card2.parse(StringIO.StringIO(caldata))

            self.assertEqual(card1, card2, "\n".join(difflib.unified_diff(str(card1).splitlines(), str(card2).splitlines())))


        def _doNonEquality(caldata):
            card1 = Card()
            card1.parse(StringIO.StringIO(caldata))

            card2 = Card()
            card2.parse(StringIO.StringIO(caldata))
            card2.addProperty(Property("X-FOO", "BAR"))

            self.assertNotEqual(card1, card2)

        for item, _ignore in self.data:
            _doEquality(item)
            _doNonEquality(item)


    def testMultiple(self):

        data = (
            (
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
""".replace("\n", "\r\n"), (
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
            )),
            (
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
BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E2:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
EMAIL;type=INTERNET;type=WORK;type=pref:athompson@example.com
FN:Another Thompson
N:Thompson;Another;;;
TEL;type=WORK;type=pref:1-555-555-5556
TEL;type=CELL:1-444-444-4445
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"), (
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
"""BEGIN:VCARD
VERSION:3.0
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E2:ABPerson
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;U
 SA
EMAIL;type=INTERNET;type=WORK;type=pref:athompson@example.com
FN:Another Thompson
N:Thompson;Another;;;
TEL;type=WORK;type=pref:1-555-555-5556
TEL;type=CELL:1-444-444-4445
item1.X-ABADR:us
END:VCARD
""".replace("\n", "\r\n"),
            )),
        )

        for item, results in data:

            cards = Card.parseMultiple(StringIO.StringIO(item))
            self.assertEqual(len(cards), len(results))
            for card, result in zip(cards, results):
                self.assertEqual(str(card), result, "\n".join(difflib.unified_diff(str(card).splitlines(), result.splitlines())))


    def testABapp(self):

        data = """BEGIN:VCARD
VERSION:3.0
N:Card;Test;;;
FN:Test Card
EMAIL;type=INTERNET;type=WORK;type=pref:sagen@apple.com
TEL;type=WORK;type=pref:555-1212
TEL;type=HOME:532-1234
PHOTO;BASE64:
  TU0AKgAAMAj////////////////////////////////////////////////////////////+///+
  SW1hZ2VNYWdpY2sgNS4zLjkgMTAvMDEvMDEgUToxNiBodHRwOi8vd3d3LmltYWdlbWFnaWNrLm9y
  ZwA=
CATEGORIES:My Contacts
X-ABUID:5B77BC10-E9DB-48C4-8BE1-BAB5E38E1E43\:ABPerson
UID:128ad7ee-a656-4773-95ce-f07f77e8cc23
REV:2011-03-23T20:20:04Z
END:VCARD
""".replace("\n", "\r\n")

        result = """BEGIN:VCARD
VERSION:3.0
UID:128ad7ee-a656-4773-95ce-f07f77e8cc23
CATEGORIES:My Contacts
EMAIL;type=INTERNET;type=WORK;type=pref:sagen@apple.com
FN:Test Card
N:Card;Test;;;
PHOTO;ENCODING=B:
 TU0AKgAAMAj////////////////////////////////////////////////////////////+
 ///+SW1hZ2VNYWdpY2sgNS4zLjkgMTAvMDEvMDEgUToxNiBodHRwOi8vd3d3LmltYWdlbWFn
 aWNrLm9yZwA=
REV:20110323T202004Z
TEL;type=WORK;type=pref:555-1212
TEL;type=HOME:532-1234
X-ABUID:5B77BC10-E9DB-48C4-8BE1-BAB5E38E1E43\:ABPerson
END:VCARD
""".replace("\n", "\r\n")

        card = Card.parseText(data)
        self.assertEqual(str(card), result)


    def testParseFail(self):

        data = (
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
""".replace("\n", "\r\n"),

"""BEGIN:VCALENDAR
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
VERSION:2.0
END:VCALENDAR
""".replace("\n", "\r\n"),

"""BOGUS
BEGIN:VCARD
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

"""BOGUS

BEGIN:VCARD
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
N:Thompson;Default;;;
FN:Default Thompson
EMAIL;type=INTERNET;type=WORK;type=pref:lthompson@example.com
TEL;type=WORK;type=pref:1-555-555-5555
TEL;type=CELL:1-444-444-4444
item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;California;11111;USA
item1.X-ABADR:us
UID:ED7A5AEC-AB19-4CE0-AD6A-2923A3E5C4E1:ABPerson
END:VCARD
BOGUS
""".replace("\n", "\r\n"),

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

BOGUS
""".replace("\n", "\r\n"),

        )

        for item in data:
            self.assertRaises(InvalidData, Card.parseText, item)


    def testParseBlank(self):

        data = (
"""
BEGIN:VCARD
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

"""

BEGIN:VCARD
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
        )

        save = ParserContext.BLANK_LINES_IN_DATA
        for item in data:
            ParserContext.BLANK_LINES_IN_DATA = ParserContext.PARSER_RAISE
            self.assertRaises(InvalidData, Card.parseText, item)

            ParserContext.BLANK_LINES_IN_DATA = ParserContext.PARSER_IGNORE
            lines = item.split("\r\n")
            result = "\r\n".join([line for line in lines if line]) + "\r\n"
            self.assertEqual(str(Card.parseText(item)), result)

        ParserContext.BLANK_LINES_IN_DATA = save
