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

from pycalendar.parameter import Parameter
from pycalendar.exceptions import InvalidProperty
from pycalendar.parser import ParserContext
from pycalendar.vcard.property import Property
import unittest

class TestProperty(unittest.TestCase):

    test_data = (
        # Different value types
        "PHOTO;VALUE=URI:http://example.com/photo.jpg",
        "photo;VALUE=URI:http://example.com/photo.jpg",
        "TEL;type=WORK;type=pref:1-555-555-5555",
        "REV:20060226T120000Z",
        "X-FOO:BAR",
        "NOTE:Some \\ntext",
        "note:Some \\ntext",
        "item1.ADR;type=WORK;type=pref:;;1245 Test;Sesame Street;CA;11111;USA",
        "X-Test:Some\, text.",
        "X-Test;VALUE=URI:geio:123.123,123.123",
        "X-ABUID:5B77BC10-E9DB-48C4-8BE1-BAB5E38E1E43\\:ABPerson",
        "X-ABUID:5B77BC10-E9DB-48C4-8BE1-BAB5E38E1E43:ABPerson",
    )

    def testParseGenerate(self):

        for data in TestProperty.test_data:
            prop = Property()
            prop.parse(data)
            propstr = str(prop)
            self.assertEqual(propstr[:-2], data, "Failed parse/generate: %s to %s" % (data, propstr,))


    def testEquality(self):

        for data in TestProperty.test_data:
            prop1 = Property()
            prop1.parse(data)
            prop2 = Property()
            prop2.parse(data)
            self.assertEqual(prop1, prop2, "Failed equality: %s" % (data,))


    def testParseBad(self):

        test_bad_data = (
            "REV:20060226T120",
            "NOTE:Some \\atext",
        )
        save = ParserContext.INVALID_ESCAPE_SEQUENCES
        for data in test_bad_data:
            ParserContext.INVALID_ESCAPE_SEQUENCES = ParserContext.PARSER_RAISE
            prop = Property()
            self.assertRaises(InvalidProperty, prop.parse, data)
        ParserContext.INVALID_ESCAPE_SEQUENCES = save


    def testHash(self):

        hashes = []
        for item in TestProperty.test_data:
            prop = Property()
            prop.parse(item)
            hashes.append(hash(prop))
        hashes.sort()
        for i in range(1, len(hashes)):
            self.assertNotEqual(hashes[i - 1], hashes[i])


    def testDefaultValueCreate(self):

        test_data = (
            ("SOURCE", "http://example.com/source", "SOURCE:http://example.com/source\r\n"),
            ("souRCE", "http://example.com/source", "souRCE:http://example.com/source\r\n"),
            ("PHOTO", "YWJj", "PHOTO:\r\n YWJj\r\n"),
            ("photo", "YWJj", "photo:\r\n YWJj\r\n"),
            ("URL", "http://example.com/tz1", "URL:http://example.com/tz1\r\n"),
        )
        for propname, propvalue, result in test_data:
            prop = Property(name=propname, value=propvalue)
            self.assertEqual(str(prop), result)


    def testParameterEncodingDecoding(self):

        prop = Property(name="X-FOO", value="Test")
        prop.addParameter(Parameter("X-BAR", "\"Check\""))
        self.assertEqual(str(prop), "X-FOO;X-BAR=^'Check^':Test\r\n")

        prop.addParameter(Parameter("X-BAR2", "Check\nThis\tOut\n"))
        self.assertEqual(str(prop), "X-FOO;X-BAR=^'Check^';X-BAR2=Check^nThis\tOut^n:Test\r\n")

        data = "X-FOO;X-BAR=^'Check^':Test"
        prop = Property()
        prop.parse(data)
        self.assertEqual(prop.getParameterValue("X-BAR"), "\"Check\"")

        data = "X-FOO;X-BAR=^'Check^';X-BAR2=Check^nThis\tOut^n:Test"
        prop = Property()
        prop.parse(data)
        self.assertEqual(prop.getParameterValue("X-BAR"), "\"Check\"")
        self.assertEqual(prop.getParameterValue("X-BAR2"), "Check\nThis\tOut\n")
