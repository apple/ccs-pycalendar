#!/usr/bin/env python
##
#    Copyright (c) 2014 Cyrus Daboo. All rights reserved.
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

from __future__ import print_function
from pycalendar.datetime import DateTime
from pycalendar.icalendar.recurrence import Recurrence
from pycalendar.period import Period
import sys

def instances(start, rrule):
    """
    Expand an RRULE.
    """

    recur = Recurrence()
    recur.parse(rrule)
    start = DateTime.parseText(start)
    end = start.duplicate()
    end.offsetYear(100)
    items = []
    range = Period(start, end)
    recur.expand(start, range, items)
    print("DTSTART:{}".format(start))
    print("RRULE:{}".format(rrule))
    print("Instances: {}".format(", ".join(map(str, items))))


if __name__ == '__main__':

    instances(sys.argv[1], sys.argv[2])
