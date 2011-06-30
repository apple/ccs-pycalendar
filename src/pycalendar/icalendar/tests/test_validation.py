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

from pycalendar.calendar import PyCalendar
from pycalendar.exceptions import PyCalendarValidationError
import unittest

class TestValidation(unittest.TestCase):
    
    def test_basic(self):
        
        data = (
            (
                "No problems",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "No PRODID",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                )),
            ),
        )
        
        for title, item, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(item)
            fixed, unfixed = cal.validate(doFix=False)
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_mode_no_fix_no_raise(self):
        
        data = (
            (
                "OK",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Unfixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                )),
            ),
            (
                "Fixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
            ),
            (
                "Fixable and unfixable",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
            ),
        )

        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=False, doRaise=False)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_mode_fix_no_raise(self):
        
        data = (
            (
                "OK",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Unfixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                )),
            ),
            (
                "Fixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                set(),
            ),
            (
                "Fixable and unfixable",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                )),
            ),
        )

        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True, doRaise=False)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_mode_no_fix_raise(self):
        
        data = (
            (
                "OK",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
                False,
            ),
            (
                "Unfixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                )),
                True,
            ),
            (
                "Fixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                True,
            ),
            (
                "Fixable and unfixable",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                True,
            ),
        )

        for title, test_old, test_new, test_fixed, test_unfixed, test_raises in data:
            cal = PyCalendar.parseText(test_old)
            if test_raises:
                self.assertRaises(PyCalendarValidationError, cal.validate, doFix=False, doRaise=True)
            else:
                try:
                    fixed, unfixed = cal.validate(doFix=False, doRaise=False)
                except:
                    self.fail(msg="Failed test: %s" % (title,))
                self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
                self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
                self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_mode_fix_raise(self):
        
        data = (
            (
                "OK",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
                False,
            ),
            (
                "Unfixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                )),
                True,
            ),
            (
                "Fixable only",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                set(),
                False,
            ),
            (
                "Fixable and unfixable",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                set((
                    "[VCALENDAR] Missing or too many required property: PRODID",
                )),
                True,
            ),
        )

        for title, test_old, test_new, test_fixed, test_unfixed, test_raises in data:
            cal = PyCalendar.parseText(test_old)
            if test_raises:
                self.assertRaises(PyCalendarValidationError, cal.validate, doFix=False, doRaise=True)
            else:
                try:
                    fixed, unfixed = cal.validate(doFix=True, doRaise=False)
                except:
                    self.fail(msg="Failed test: %s" % (title,))
                self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
                self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
                self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_vevent(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VEVENT] Missing or too many required property: DTSTAMP",
                )),
            ),
            (
                "Too many",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
UID:C3184A66-1ED0-11D9-A5E0-000A958A3253
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
SUMMARY:New Year's Eve
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
UID:C3184A66-1ED0-11D9-A5E0-000A958A3253
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
SUMMARY:New Year's Eve
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VEVENT] Missing or too many required property: UID",
                    "[VEVENT] Too many properties present: SUMMARY",
                )),
            ),
            (
                "PROP value",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VEVENT] Property value incorrect: DTSTAMP",
                )),
            ),
            (
                "No DTSTART without METHOD",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:CANCEL
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTAMP:20020101T000000Z
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:CANCEL
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTAMP:20020101T000000Z
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Combo fix",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                set(),
            ),
            (
                "Mismatch UNTIL as DATE-TIME",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231T120000;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Value types must match: DTSTART, UNTIL",
                )),
                set(),
            ),
            (
                "Mismatch UNTIL as DATE",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART:20020101T121212Z
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART:20020101T121212Z
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231T121212Z;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Value types must match: DTSTART, UNTIL",
                )),
                set(),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_vfreebusy(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VFREEBUSY
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
END:VFREEBUSY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VFREEBUSY
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
END:VFREEBUSY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VFREEBUSY
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
END:VFREEBUSY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VFREEBUSY
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
END:VFREEBUSY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VFREEBUSY] Missing or too many required property: DTSTAMP",
                )),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_vjournal(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VJOURNAL
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTSTAMP:20020101T000000Z
END:VJOURNAL
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VJOURNAL
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTSTAMP:20020101T000000Z
END:VJOURNAL
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VJOURNAL
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
END:VJOURNAL
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VJOURNAL
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
END:VJOURNAL
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VJOURNAL] Missing or too many required property: DTSTAMP",
                )),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_vtimezone(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTIMEZONE
TZID:America/New_York
LAST-MODIFIED:20050809T050000Z
BEGIN:DAYLIGHT
DTSTART:19670430T020000
RRULE:FREQ=YEARLY;UNTIL=19730429T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;UNTIL=20061029T060000Z;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTIMEZONE
TZID:America/New_York
LAST-MODIFIED:20050809T050000Z
BEGIN:DAYLIGHT
DTSTART:19670430T020000
RRULE:FREQ=YEARLY;UNTIL=19730429T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;UNTIL=20061029T060000Z;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTIMEZONE
LAST-MODIFIED:20050809T050000Z
BEGIN:DAYLIGHT
DTSTART:19670430T020000
RRULE:FREQ=YEARLY;UNTIL=19730429T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;UNTIL=20061029T060000Z;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTIMEZONE
LAST-MODIFIED:20050809T050000Z
BEGIN:DAYLIGHT
DTSTART:19670430T020000
RRULE:FREQ=YEARLY;UNTIL=19730429T070000Z;BYDAY=-1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:19671029T020000
RRULE:FREQ=YEARLY;UNTIL=20061029T060000Z;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VTIMEZONE] Missing or too many required property: TZID",
                )),
            ),
            (
                "Missing components",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTIMEZONE
TZID:America/New_York
LAST-MODIFIED:20050809T050000Z
END:VTIMEZONE
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTIMEZONE
TZID:America/New_York
LAST-MODIFIED:20050809T050000Z
END:VTIMEZONE
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VTIMEZONE] At least one component must be present: STANDARD or DAYLIGHT",
                )),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_vtodo(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VTODO] Missing or too many required property: DTSTAMP",
                )),
            ),
            (
                "Too many",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
UID:C3184A66-1ED0-11D9-A5E0-000A958A3253
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
SUMMARY:New Year's Eve
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
UID:C3184A66-1ED0-11D9-A5E0-000A958A3253
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
SUMMARY:New Year's Eve
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VTODO] Missing or too many required property: UID",
                    "[VTODO] Too many properties present: SUMMARY",
                )),
            ),
            (
                "PROP value",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VTODO] Property value incorrect: DTSTAMP",
                )),
            ),
            (
                "DURATION without DTSTART",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VTODO] Property must be present: DTSTART with DURATION",
                )),
            ),
            (
                "Combo fix",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VTODO
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DUE;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VTODO
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VTODO] Properties must not both be present: DUE, DURATION",
                )),
                set(),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_vavailability(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VAVAILABILITY] Missing or too many required property: DTSTAMP",
                )),
            ),
            (
                "Too many",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VAVAILABILITY] Missing or too many required property: UID",
                    "[VAVAILABILITY] Too many properties present: ORGANIZER",
                )),
            ),
            (
                "Combo fix",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DURATION:P1D
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DURATION:P1D
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VAVAILABILITY] Properties must not both be present: DTEND, DURATION",
                )),
                set(),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_available(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[AVAILABLE] Missing or too many required property: DTSTAMP",
                )),
            ),
            (
                "Too many",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
SUMMARY:Monday to Friday from 9 am to 5 pm
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
SUMMARY:Monday to Friday from 9 am to 5 pm
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[AVAILABLE] Missing or too many required property: UID",
                    "[AVAILABLE] Too many properties present: SUMMARY",
                )),
            ),
            (
                "Combo fix",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DURATION:P1D
DTEND;TZID=America/Montreal:20111002T170000
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VAVAILABILITY
UID:20111005T133225Z-00001@example.com
DTSTAMP:20111005T133225Z
ORGANIZER:mailto:bernard@example.com
BEGIN:AVAILABLE
UID:20111005T133225Z-00001-A@example.com
DTSTART;TZID=America/Montreal:20111002T090000
DURATION:P1D
DTSTAMP:20111005T133225Z
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
SUMMARY:Monday to Friday from 9:00 to 17:00
END:AVAILABLE
END:VAVAILABILITY
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[AVAILABLE] Properties must not both be present: DTEND, DURATION",
                )),
                set(),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_valarm(self):
        data = (
            (
                "No problem",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Missing required",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VALARM] Missing or too many required property: TRIGGER",
                )),
            ),
            (
                "Too many",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:AUDIO
ATTACH:http://example.com/audio/boink
ATTACH:http://example.com/audio/quack
TRIGGER:-PT15M
TRIGGER:-PT30M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:AUDIO
ATTACH:http://example.com/audio/boink
ATTACH:http://example.com/audio/quack
TRIGGER:-PT15M
TRIGGER:-PT30M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VALARM] Missing or too many required property: TRIGGER",
                    "[VALARM] Too many properties present: ATTACH",
                )),
            ),
            (
                "Too few",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:EMAIL
DESCRIPTION:Reminder
SUMMARY:Reminder
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:EMAIL
DESCRIPTION:Reminder
SUMMARY:Reminder
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VALARM] Missing required property: ATTENDEE",
                )),
            ),
            (
                "PROP value",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
DURATION:-P1D
REPEAT:-1
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
DURATION:-P1D
REPEAT:-1
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VALARM] Property value incorrect: REPEAT",
                )),
            ),
            (
                "DUARTION and REPEAT together",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:CANCEL
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
REPEAT:2
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:CANCEL
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
REPEAT:2
TRIGGER:-PT15M
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[VALARM] Properties must be present together: DURATION, REPEAT",
                )),
            ),
            (
                "Combo fix",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DURATION:P1D
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set((
                    "[VEVENT] Properties must not both be present: DTEND, DURATION",
                )),
                set((
                    "[VALARM] Missing or too many required property: TRIGGER",
                )),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

    def test_xcomponents(self):
        data = (
            (
                "No problem #1",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
BEGIN:X-COMPONENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
SUMMARY:New Year's Day
END:X-COMPONENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
BEGIN:X-COMPONENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
SUMMARY:New Year's Day
END:X-COMPONENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "No problem #2",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
BEGIN:X-COMPONENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTEND;VALUE=DATE:20020102
DTSTART;VALUE=DATE:20020101
DURATION:P1D
SUMMARY:New Year's Day
END:X-COMPONENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
BEGIN:X-COMPONENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTEND;VALUE=DATE:20020102
DTSTART;VALUE=DATE:20020101
DURATION:P1D
SUMMARY:New Year's Day
END:X-COMPONENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set(),
            ),
            (
                "Prop value",
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
BEGIN:X-COMPONENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000
DTSTART;VALUE=DATE:20020101
SUMMARY:New Year's Day
END:X-COMPONENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//mulberrymail.com//Mulberry v4.0//EN
BEGIN:VEVENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTSTART;VALUE=DATE:20020101
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000Z
RRULE:FREQ=YEARLY;UNTIL=20031231;BYMONTH=1
SUMMARY:New Year's Day
END:VEVENT
BEGIN:X-COMPONENT
UID:C3184A66-1ED0-11D9-A5E0-000A958A3252
DTEND;VALUE=DATE:20020102
DTSTAMP:20020101T000000
DTSTART;VALUE=DATE:20020101
SUMMARY:New Year's Day
END:X-COMPONENT
END:VCALENDAR
""".replace("\n", "\r\n"),
                set(),
                set((
                    "[X-COMPONENT] Property value incorrect: DTSTAMP",
                )),
            ),
        )
        
        for title, test_old, test_new, test_fixed, test_unfixed in data:
            cal = PyCalendar.parseText(test_old)
            fixed, unfixed = cal.validate(doFix=True)
            self.assertEqual(str(cal), test_new, msg="Failed test: %s" % (title,))
            self.assertEqual(set(fixed), test_fixed, msg="Failed test: %s" % (title,))
            self.assertEqual(set(unfixed), test_unfixed, msg="Failed test: %s" % (title,))

