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

from pycalendar.attribute import PyCalendarAttribute
from pycalendar.exceptions import PyCalendarInvalidProperty
from pycalendar.parser import ParserContext
from pycalendar.property import PyCalendarProperty
from pycalendar.value import PyCalendarValue
import unittest

class TestProperty(unittest.TestCase):

    test_data = (
        # Different value types
        "ATTACH;VALUE=BINARY:VGVzdA==",
        "attach;VALUE=BINARY:VGVzdA==",
        "ORGANIZER:mailto:jdoe@example.com",
        "DTSTART;TZID=US/Eastern:20060226T120000",
        "DTSTART;VALUE=DATE:20060226",
        "DTSTART:20060226T130000Z",
        "X-FOO:BAR",
        "DURATION:PT10M",
        "duraTION:PT10M",
        "SEQUENCE:1",
        "RDATE:20060226T120000Z,20060227T120000Z",
        "FREEBUSY:20060226T120000Z/20060227T120000Z",
        "SUMMARY:Some \\ntext",
        "RRULE:FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,TH;BYSETPOS=-1",
        "REQUEST-STATUS:2.0;Success",
        "URI:http://www.example.com",
        "TZOFFSETFROM:-0500",
        "X-Test:Some\, text.",
        "X-Test:Some:, text.",
        "X-APPLE-STRUCTURED-LOCATION;VALUE=URI:geo:123.123,123.123",
        "X-CALENDARSERVER-PRIVATE-COMMENT:This\\ntest\\nis\\, here.\\n",

        # Various parameters
        "DTSTART;TZID=\"Somewhere, else\":20060226T120000",
        "ATTENDEE;PARTSTAT=ACCEPTED;ROLE=CHAIR:mailto:jdoe@example.com",
        "X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-APPLE-ABUID=ab\\://Work;X-TITLE=\"10\\n XX S. XXX Dr.\\nSuite XXX\\nXX XX XXXXX\\nUnited States\":\"geo:11.111111,-11.111111\"",

        # Parameter escaping
        "ATTENDEE;CN=My ^'Test^' Name;ROLE=CHAIR:mailto:jdoe@example.com",
    )


    def testParseGenerate(self):

        for data in TestProperty.test_data:
            prop = PyCalendarProperty()
            prop.parse(data)
            propstr = str(prop).replace("\r\n ", "")
            self.assertEqual(propstr[:-2], data, "Failed parse/generate: %s to %s" % (data, propstr,))


    def testEquality(self):

        for data in TestProperty.test_data:
            prop1 = PyCalendarProperty()
            prop1.parse(data)
            prop2 = PyCalendarProperty()
            prop2.parse(data)
            self.assertEqual(prop1, prop2, "Failed equality: %s" % (data,))


    def testParseBad(self):

        test_bad_data = (
            "DTSTART;TZID=US/Eastern:abc",
            "DTSTART;VALUE=DATE:20060226T",
            "DTSTART:20060226T120000A",
            "X-FOO;:BAR",
            "DURATION:A",
            "SEQUENCE:b",
            "RDATE:20060226T120000Z;20060227T120000Z",
            "FREEBUSY:20060226T120000Z/ABC",
            "SUMMARY:Some \\qtext",
            "RRULE:FREQ=MONTHLY;COUNT=3;BYDAY=TU,WE,VE;BYSETPOS=-1",
            "TZOFFSETFROM:-050",
            """ATTENDEE;CN="\\";CUTYPE=INDIVIDUAL;PARTSTAT=X-UNDELIVERABLE:invalid:nomai
 l""",
        )
        save = ParserContext.INVALID_ESCAPE_SEQUENCES
        for data in test_bad_data:
            ParserContext.INVALID_ESCAPE_SEQUENCES = ParserContext.PARSER_RAISE
            prop = PyCalendarProperty()
            self.assertRaises(PyCalendarInvalidProperty, prop.parse, data)
        ParserContext.INVALID_ESCAPE_SEQUENCES = save


    def testHash(self):

        hashes = []
        for item in TestProperty.test_data:
            prop = PyCalendarProperty()
            prop.parse(item)
            hashes.append(hash(prop))
        hashes.sort()
        for i in range(1, len(hashes)):
            self.assertNotEqual(hashes[i - 1], hashes[i])


    def testDefaultValueCreate(self):

        test_data = (
            ("ATTENDEE", "mailto:attendee@example.com", "ATTENDEE:mailto:attendee@example.com\r\n"),
            ("attendee", "mailto:attendee@example.com", "attendee:mailto:attendee@example.com\r\n"),
            ("ORGANIZER", "mailto:organizer@example.com", "ORGANIZER:mailto:organizer@example.com\r\n"),
            ("ORGANizer", "mailto:organizer@example.com", "ORGANizer:mailto:organizer@example.com\r\n"),
            ("URL", "http://example.com/tz1", "URL:http://example.com/tz1\r\n"),
            ("TZURL", "http://example.com/tz2", "TZURL:http://example.com/tz2\r\n"),
        )
        for propname, propvalue, result in test_data:
            prop = PyCalendarProperty(name=propname, value=propvalue)
            self.assertEqual(str(prop), result)


    def testGEOValueRoundtrip(self):

        data = "GEO:123.456,789.101"
        prop = PyCalendarProperty()
        prop.parse(data)
        self.assertEqual(str(prop), data + "\r\n")


    def testUnknownValueRoundtrip(self):

        data = "X-FOO:Text, not escaped"
        prop = PyCalendarProperty()
        prop.parse(data)
        self.assertEqual(str(prop), data + "\r\n")

        prop = PyCalendarProperty("X-FOO", "Text, not escaped")
        self.assertEqual(str(prop), data + "\r\n")

        data = "X-FOO:Text\\, escaped\\n"
        prop = PyCalendarProperty()
        prop.parse(data)
        self.assertEqual(str(prop), data + "\r\n")

        prop = PyCalendarProperty("X-FOO", "Text\\, escaped\\n")
        self.assertEqual(str(prop), data + "\r\n")


    def testNewRegistrationValueRoundtrip(self):

        PyCalendarProperty.registerDefaultValue("X-SPECIAL-REGISTRATION", PyCalendarValue.VALUETYPE_TEXT)

        data = "X-SPECIAL-REGISTRATION:Text\\, escaped\\n"
        prop = PyCalendarProperty()
        prop.parse(data)
        self.assertEqual(str(prop), "X-SPECIAL-REGISTRATION:Text\\, escaped\\n\r\n")

        prop = PyCalendarProperty("X-SPECIAL-REGISTRATION", "Text, escaped\n")
        self.assertEqual(str(prop), "X-SPECIAL-REGISTRATION:Text\\, escaped\\n\r\n")


    def testParameterEncodingDecoding(self):

        prop = PyCalendarProperty("X-FOO", "Test")
        prop.addAttribute(PyCalendarAttribute("X-BAR", "\"Check\""))
        self.assertEqual(str(prop), "X-FOO;X-BAR=^'Check^':Test\r\n")

        prop.addAttribute(PyCalendarAttribute("X-BAR2", "Check\nThis\tOut\n"))
        self.assertEqual(str(prop), "X-FOO;X-BAR=^'Check^';X-BAR2=Check^nThis^tOut^n:Test\r\n")

        data = "X-FOO;X-BAR=^'Check^':Test"
        prop = PyCalendarProperty()
        prop.parse(data)
        self.assertEqual(prop.getAttributeValue("X-BAR"), "\"Check\"")

        data = "X-FOO;X-BAR=^'Check^';X-BAR2=Check^nThis^tOut^n:Test"
        prop = PyCalendarProperty()
        prop.parse(data)
        self.assertEqual(prop.getAttributeValue("X-BAR"), "\"Check\"")
        self.assertEqual(prop.getAttributeValue("X-BAR2"), "Check\nThis\tOut\n")
