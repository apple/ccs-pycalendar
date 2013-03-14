#!/usr/bin/env python
##
#    Copyright (c) 2012 Cyrus Daboo. All rights reserved.
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
from pycalendar.exceptions import PyCalendarError
from pycalendar.parser import ParserContext
from pycalendar.vcard.card import Card
import os
import sys

def validate(fname):
    """
    Check whether the contents of the specified file is valid iCalendar or vCard data.
    """

    data = open(fname).read()

    ParserContext.allRaise()

    if data.find("BEGIN:VCALENDAR") != -1:
        try:
            cal = PyCalendar.parseText(data)
        except PyCalendarError, e:
            print "Failed to parse iCalendar: %r" % (e,)
            sys.exit(1)
    elif data.find("BEGIN:VCARD") != -1:
        try:
            cal = Card.parseText(data)
        except PyCalendarError, e:
            print "Failed to parse vCard: %r" % (e,)
            sys.exit(1)
    else:
        print "Failed to find valid iCalendar or vCard data"
        sys.exit(1)

    _ignore_fixed, unfixed = cal.validate(doFix=False, doRaise=False)
    if unfixed:
        print "List of problems: %s" % (unfixed,)
    else:
        print "No problems"

    # Control character check - only HTAB, CR, LF allowed for characters in the range 0x00-0x1F
    s = str(data)
    if len(s.translate(None, "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0B\x0C\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F")) != len(s):
        for ctr, i in enumerate(data):
            if i in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0B\x0C\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F":
                print "Control character %d at position %d" % (ord(i), ctr,)


if __name__ == '__main__':

    fname = os.path.expanduser(sys.argv[1])
    validate(fname)
