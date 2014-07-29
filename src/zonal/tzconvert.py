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

from __future__ import with_statement
from __future__ import print_function

from pycalendar.icalendar.calendar import Calendar
from xml.etree.cElementTree import ParseError as XMLParseError
import cStringIO as StringIO
import getopt
import os
import rule
import sys
import tarfile
import urllib
import xml.etree.cElementTree as XML
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
            print("Failed to parse file %s" % (file,))
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
            if nextline.startswith("\t") or nextline.startswith(" "):
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


    def parseWindowsAliases(self, aliases):

        try:
            xmlfile = open(aliases)
            xmlroot = XML.ElementTree(file=xmlfile).getroot()
        except (IOError, XMLParseError):
            raise ValueError("Unable to open or read windows alias file: {}".format(aliases))

        # Extract the mappings
        try:
            for elem in xmlroot.findall("./windowsZones/mapTimezones/mapZone"):
                if elem.get("territory", "") == "001":
                    if elem.get("other") not in self.links:
                        self.links[elem.get("other")] = elem.get("type")
                    else:
                        print("Ignoring duplicate Windows alias: {}".format(elem.get("other")))
        except (ValueError, KeyError):
            raise ValueError("Unable to parse windows alias file: {}".format(aliases))


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

        cal = Calendar()
        for zone in self.zones.itervalues():
            if filterzones and zone.name not in filterzones:
                continue
            vtz = zone.vtimezone(cal, self.rules, minYear, maxYear)
            cal.addComponent(vtz)

        return cal.getText()


    def generateZoneinfoFiles(self, outputdir, minYear, maxYear=2018, links=True, windowsAliases=None, filterzones=None):

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
            cal = Calendar()
            vtz = zone.vtimezone(cal, self.rules, minYear, maxYear)
            cal.addComponent(vtz)

            icsdata = cal.getText()
            fpath = os.path.join(outputdir, zone.name + ".ics")
            if not os.path.exists(os.path.dirname(fpath)):
                os.makedirs(os.path.dirname(fpath))
            with open(fpath, "w") as f:
                f.write(icsdata)
            if self.verbose:
                print("Write path: %s" % (fpath,))

        if links:
            if windowsAliases is not None:
                self.parseWindowsAliases(windowsAliases)

            link_list = []
            for linkTo, linkFrom in sorted(self.links.iteritems(), key=lambda x: x[0]):

                # Check for existing output file
                fromPath = os.path.join(outputdir, linkFrom + ".ics")
                if not os.path.exists(fromPath):
                    print("Missing link from: %s to %s" % (linkFrom, linkTo,))
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
                    print("Write link: %s" % (linkTo,))

                link_list.append("%s\t%s" % (linkTo, linkFrom,))

            # Generate link mapping file
            linkPath = os.path.join(outputdir, "links.txt")
            open(linkPath, "w").write("\n".join(link_list))



def usage(error_msg=None):
    if error_msg:
        print(error_msg)

    print("""Usage: tzconvert [options] [DIR]
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

""")

    if error_msg:
        raise ValueError(error_msg)
    else:
        sys.exit(0)


if __name__ == '__main__':

    # Set the PRODID value used in generated iCalendar data
    prodid = "-//mulberrymail.com//Zonal//EN"
    rootdir = "../../temp"
    startYear = 1800
    endYear = 2018
    windowsAliases = None

    options, args = getopt.getopt(sys.argv[1:], "h", ["prodid=", "root=", "start=", "end=", "windows="])

    for option, value in options:
        if option == "-h":
            usage()
        elif option == "--prodid":
            prodid = value
        elif option == "--root":
            rootdir = os.path.expanduser(value)
        elif option == "--start":
            startYear = int(value)
        elif option == "--end":
            endYear = int(value)
        elif option == "--windows":
            windowsAliases = os.path.expanduser(value)
        else:
            usage("Unrecognized option: %s" % (option,))

    if not os.path.exists(rootdir):
        os.makedirs(rootdir)
    zonedir = os.path.join(rootdir, "tzdata")
    if not os.path.exists(zonedir):
        print("Downloading and extracting IANA timezone database")
        os.mkdir(zonedir)
        iana = "https://www.iana.org/time-zones/repository/tzdata-latest.tar.gz"
        data = urllib.urlretrieve(iana)
        print("Extract data at: %s" % (data[0]))
        with tarfile.open(data[0], "r:gz") as t:
            t.extractall(zonedir)

    if windowsAliases is None:
        windowsAliases = os.path.join(rootdir, "windowsZones.xml")
    if not os.path.exists(windowsAliases):
        print("Downloading Unicode database")
        unicode = "http://unicode.org/repos/cldr/tags/latest/common/supplemental/windowsZones.xml"
        data = urllib.urlretrieve(unicode, windowsAliases)

    Calendar.sProdID = prodid

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

    parser.generateZoneinfoFiles(
        os.path.join(rootdir, "zoneinfo"),
        startYear,
        endYear,
        windowsAliases=windowsAliases,
        filterzones=(
            # "America/Montevideo",
            # "Europe/Paris",
            # "Africa/Cairo",
        )
    )
