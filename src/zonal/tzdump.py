#!/usr/bin/env python
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

from __future__ import print_function
from pycalendar.datetime import DateTime
from pycalendar.exceptions import InvalidData
from pycalendar.icalendar.calendar import Calendar
import getopt
import os
import sys


def loadCalendar(file, verbose):

    cal = Calendar()
    if verbose:
        print("Parsing calendar data: %s" % (file,))
    with open(file, "r") as fin:
        try:
            cal.parse(fin)
        except InvalidData as e:
            print("Failed to parse bad data: %s" % (e.mData,))
            raise
    return cal


def getExpandedDates(cal, start, end):

    vtz = cal.getComponents()[0]
    expanded = vtz.expandAll(start, end)
    expanded.sort(cmp=lambda x, y: DateTime.sort(x[0], y[0]))
    return expanded


def sortedList(setdata):
    l = list(setdata)
    l.sort(cmp=lambda x, y: DateTime.sort(x[0], y[0]))
    return l


def formattedExpandedDates(expanded):
    items = sortedList([(item[0], item[1], secondsToTime(item[2]), secondsToTime(item[3]),) for item in expanded])
    return ", ".join(["(%s, %s, %s, %s)" % item for item in items])


def secondsToTime(seconds):
    if seconds < 0:
        seconds = -seconds
        negative = "-"
    else:
        negative = ""
    secs = divmod(seconds, 60)[1]
    mins = divmod(seconds / 60, 60)[1]
    hours = divmod(seconds / (60 * 60), 60)[1]
    if secs:
        return "%s%02d:%02d:%02d" % (negative, hours, mins, secs,)
    else:
        return "%s%02d:%02d" % (negative, hours, mins,)


def usage(error_msg=None):
    if error_msg:
        print(error_msg)

    print("""Usage: tzdump [options] FILE
Options:
    -h            Print this help and exit
    -v            Be verbose
    --start       Start year
    --end         End year

Arguments:
    FILE          iCalendar file containing a single VTIMEZONE

Description:
    This utility will dump the transitions in a VTIMEZONE over
    the request time range.

""")

    if error_msg:
        raise ValueError(error_msg)
    else:
        sys.exit(0)


if __name__ == '__main__':

    verbose = False
    startYear = 1918
    endYear = 2018
    fpath = None

    options, args = getopt.getopt(sys.argv[1:], "hv", ["start=", "end=", ])

    for option, value in options:
        if option == "-h":
            usage()
        elif option == "-v":
            verbose = True
        elif option == "--start":
            startYear = int(value)
        elif option == "--end":
            endYear = int(value)
        else:
            usage("Unrecognized option: %s" % (option,))

    # Process arguments
    if len(args) != 1:
        usage("Must have one argument")
    fpath = os.path.expanduser(args[0])

    start = DateTime(year=startYear, month=1, day=1)
    end = DateTime(year=endYear, month=1, day=1)

    cal = loadCalendar(fpath, verbose)
    dates = getExpandedDates(cal, start, end)
    print(formattedExpandedDates(dates))
