#!/usr/bin/env python
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

from __future__ import with_statement

from difflib import unified_diff
from pycalendar.calendar import PyCalendar
import cStringIO as StringIO
import getopt
import os
import rule
import sys
import zone

"""
Classes to parse a tzdata files and generate VTIMEZONE data.
"""

__all__ = (
    "tzconvert",
)

class tzconvert(object):

    def __init__(self, verbose=False):
        self.rules = {}
        self.zones = {}
        self.links = {}
        self.verbose = verbose


    def getZoneNames(self):
        return set(self.zones.keys())


    def parse(self, file):
        try:
            f = open(file, "r")
            ctr = 0
            for line in f:
                ctr += 1
                line = line[:-1]
                while True:
                    if line.startswith("#") or len(line) == 0:
                        break
                    elif line.startswith("Rule"):
                        self.parseRule(line)
                        break
                    elif line.startswith("Zone"):
                        line = self.parseZone(line, f)
                        if line is None:
                            break
                    elif line.startswith("Link"):
                        self.parseLink(line)
                        break
                    elif len(line.strip()) != 0:
                        assert False, "Could not parse line %d from tzconvert file: '%s'" % (ctr, line,)
                    else:
                        break
        except:
            print "Failed to parse file %s" % (file,)
            raise


    def parseRule(self, line):
        ruleitem = rule.Rule()
        ruleitem.parse(line)
        self.rules.setdefault(ruleitem.name, rule.RuleSet()).rules.append(ruleitem)


    def parseZone(self, line, f):
        os = StringIO.StringIO()
        os.write(line)
        last_line = None
        for nextline in f:
            nextline = nextline[:-1]
            if nextline.startswith("\t"):
                os.write("\n")
                os.write(nextline)
            elif nextline.startswith("#") or len(nextline) == 0:
                continue
            else:
                last_line = nextline
                break

        zoneitem = zone.Zone()
        zoneitem.parse(os.getvalue())
        self.zones[zoneitem.name] = zoneitem

        return last_line


    def parseLink(self, line):

        splits = line.split()
        linkFrom = splits[1]
        linkTo = splits[2]
        self.links[linkTo] = linkFrom


    def expandZone(self, zonename, minYear, maxYear=2018):
        """
        Expand a zones transition dates up to the specified year.
        """
        zone = self.zones[zonename]
        expanded = zone.expand(self.rules, minYear, maxYear)
        return [(item[0], item[1], item[2],) for item in expanded]


    def vtimezones(self, minYear, maxYear=2018, filterzones=None):
        """
        Generate iCalendar data for all VTIMEZONEs or just those specified
        """

        cal = PyCalendar()
        for zone in self.zones.itervalues():
            if filterzones and zone.name not in filterzones:
                continue
            vtz = zone.vtimezone(cal, self.rules, minYear, maxYear)
            cal.addComponent(vtz)

        return cal.getText()


    def generateZoneinfoFiles(self, outputdir, minYear, maxYear=2018, links=True, filterzones=None):

        # Empty current directory
        try:
            for root, dirs, files in os.walk(outputdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        except OSError:
            pass

        for zone in self.zones.itervalues():
            if filterzones and zone.name not in filterzones:
                continue
            cal = PyCalendar()
            vtz = zone.vtimezone(cal, self.rules, minYear, maxYear)
            cal.addComponent(vtz)

            icsdata = cal.getText()
            fpath = os.path.join(outputdir, zone.name + ".ics")
            if not os.path.exists(os.path.dirname(fpath)):
                os.makedirs(os.path.dirname(fpath))
            with open(fpath, "w") as f:
                f.write(icsdata)
            if self.verbose:
                print "Write path: %s" % (fpath,)

        if links:
            link_list = []
            for linkTo, linkFrom in self.links.iteritems():

                # Check for existing output file
                fromPath = os.path.join(outputdir, linkFrom + ".ics")
                if not os.path.exists(fromPath):
                    print "Missing link from: %s to %s" % (linkFrom, linkTo,)
                    continue

                with open(fromPath) as f:
                    icsdata = f.read()
                icsdata = icsdata.replace(linkFrom, linkTo)

                toPath = os.path.join(outputdir, linkTo + ".ics")
                if not os.path.exists(os.path.dirname(toPath)):
                    os.makedirs(os.path.dirname(toPath))
                with open(toPath, "w") as f:
                    f.write(icsdata)
                if self.verbose:
                    print "Write link: %s" % (linkTo,)

                link_list.append("%s\t%s" % (linkTo, linkFrom,))

            # Generate link mapping file
            linkPath = os.path.join(outputdir, "links.txt")
            open(linkPath, "w").write("\n".join(link_list))



def usage(error_msg=None):
    if error_msg:
        print error_msg

    print """Usage: tzconvert [options] [DIR]
Options:
    -h            Print this help and exit
    --prodid      PROD-ID string to use
    --start       Start year
    --end         End year

Arguments:
    DIR      Directory containing an Olson tzdata directory to read, also
             where zoneinfo data will be written

Description:
    This utility convert Olson-style timezone data in iCalendar.
    VTIMEZONE objects, one .ics file per-timezone.

"""

    if error_msg:
        raise ValueError(error_msg)
    else:
        sys.exit(0)


if __name__ == '__main__':

    # Set the PRODID value used in generated iCalendar data
    prodid = "-//mulberrymail.com//Zonal//EN"
    rootdir = "../../stuff/temp"
    startYear = 1800
    endYear = 2018

    options, args = getopt.getopt(sys.argv[1:], "h", ["prodid=", "root=", "start=", "end=", ])

    for option, value in options:
        if option == "-h":
            usage()
        elif option == "--prodid":
            prodid = value
        elif option == "--root":
            rootdir = value
        elif option == "--start":
            startYear = int(value)
        elif option == "--end":
            endYear = int(value)
        else:
            usage("Unrecognized option: %s" % (option,))

    # Process arguments
    if len(args) > 1:
        usage("Must have only one argument")
    if len(args) == 1:
        rootdir = os.path.expanduser(args[0])

    PyCalendar.sProdID = prodid

    zonedir = os.path.join(rootdir, "tzdata")
    zonefiles = (
        "northamerica",
        "southamerica",
        "europe",
        "africa",
        "asia",
        "australasia",
        "antarctica",
        "etcetera",
        "backward",
    )

    parser = tzconvert(verbose=True)
    for file in zonefiles:
        parser.parse(os.path.join(zonedir, file))

    if 1:
        parser.generateZoneinfoFiles(os.path.join(rootdir, "zoneinfo"), startYear, endYear, filterzones=(
            #"America/Montevideo",
            #"Europe/Paris",
            #"Africa/Cairo",
        ))

    if 0:
        checkName = "EST"
        parsed = parser.vtimezones(1800, 2018, filterzones=(
            checkName,
        ))

        icsdir = "../2008i/zoneinfo"
        cal = PyCalendar()
        for file in (checkName,):
            fin = open(os.path.join(icsdir, file + ".ics"), "r")
            cal.parse(fin)

        for vtz in cal.getVTimezoneDB():
            #from pycalendar.vtimezoneelement import PyCalendarVTimezoneElement
            #vtz.mEmbedded.sort(PyCalendarVTimezoneElement.sort_dtstart)
            for embedded in vtz.mEmbedded:
                embedded.finalise()
            vtz.finalise()

        os = StringIO.StringIO()
        cal.generate(os, False)
        actual = os.getvalue()

        print "-- ACTUAL --"
        print actual
        print
        print "-- PARSED --"
        print parsed
        print
        print "-- DIFF --"
        print "\n".join([line for line in unified_diff(actual.split("\n"), parsed.split("\n"))])
