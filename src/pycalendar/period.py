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

from pycalendar import xmldefs
from pycalendar.datetime import PyCalendarDateTime
from pycalendar.duration import PyCalendarDuration
from pycalendar.valueutils import ValueMixin
import xml.etree.cElementTree as XML

class PyCalendarPeriod(ValueMixin):

    def __init__(self, start=None, end=None, duration=None):

        self.mStart = start if start is not None else PyCalendarDateTime()

        if end is not None:
            self.mEnd = end
            self.mDuration = self.mEnd - self.mStart
            self.mUseDuration = False
        elif duration is not None:
            self.mDuration = duration
            self.mEnd = self.mStart + self.mDuration
            self.mUseDuration = True
        else:
            self.mEnd = self.mStart.duplicate()
            self.mDuration = PyCalendarDuration()
            self.mUseDuration = False


    def duplicate(self):
        other = PyCalendarPeriod(start=self.mStart.duplicate(), end=self.mEnd.duplicate())
        other.mUseDuration = self.mUseDuration
        return other


    def __hash__(self):
        return hash((self.mStart, self.mEnd,))


    def __repr__(self):
        return "PyCalendarPeriod %s" % (self.getText(),)


    def __str__(self):
        return self.getText()


    def __eq__(self, comp):
        return self.mStart == comp.mStart and self.mEnd == comp.mEnd


    def __gt__(self, comp):
        return self.mStart > comp


    def __lt__(self, comp):
        return self.mStart < comp.mStart  \
                or (self.mStart == comp.mStart) and self.mEnd < comp.mEnd


    def parse(self, data):
        splits = data.split('/', 1)
        if len(splits) == 2:
            start = splits[0]
            end = splits[1]

            self.mStart.parse(start)
            if end[0] == 'P':
                self.mDuration.parse(end)
                self.mUseDuration = True
                self.mEnd = self.mStart + self.mDuration
            else:
                self.mEnd.parse(end)
                self.mUseDuration = False
                self.mDuration = self.mEnd - self.mStart
        else:
            raise ValueError


    def generate(self, os):
        try:
            self.mStart.generate(os)
            os.write("/")
            if self.mUseDuration:
                self.mDuration.generate(os)
            else:
                self.mEnd.generate(os)
        except:
            pass


    def writeXML(self, node, namespace):
        start = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.period_start))
        start.text = self.mStart.getXMLText()

        if self.mUseDuration:
            duration = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.period_duration))
            duration.text = self.mDuration.getText()
        else:
            end = XML.SubElement(node, xmldefs.makeTag(namespace, xmldefs.period_end))
            end.text = self.mEnd.getXMLText()


    def getStart(self):
        return self.mStart


    def getEnd(self):
        return self.mEnd


    def getDuration(self):
        return self.mDuration


    def getUseDuration(self):
        return self.mUseDuration


    def setUseDuration(self, use):
        self.mUseDuration = use


    def isDateWithinPeriod(self, dt):
        # Inclusive start, exclusive end
        return dt >= self.mStart and dt < self.mEnd


    def isDateBeforePeriod(self, dt):
        # Inclusive start
        return dt < self.mStart


    def isDateAfterPeriod(self, dt):
        # Exclusive end
        return dt >= self.mEnd


    def isPeriodOverlap(self, p):
        # Inclusive start, exclusive end
        return not (self.mStart >= p.mEnd or self.mEnd <= p.mStart)


    def adjustToUTC(self):
        self.mStart.adjustToUTC()
        self.mEnd.adjustToUTC()


    def describeDuration(self):
        return ""
