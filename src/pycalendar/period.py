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

from pycalendar import xmldefinitions, xmlutils
from pycalendar.datetime import DateTime
from pycalendar.duration import Duration
from pycalendar.valueutils import ValueMixin
import xml.etree.cElementTree as XML

class Period(ValueMixin):

    def __init__(self, start=None, end=None, duration=None):

        self.mStart = start if start is not None else DateTime()

        if end is not None:
            self.mEnd = end
            self.mDuration = None
            self.mUseDuration = False
        elif duration is not None:
            self.mDuration = duration
            self.mEnd = None
            self.mUseDuration = True
        else:
            self.mEnd = self.mStart.duplicate()
            self.mDuration = None
            self.mUseDuration = False


    def duplicate(self):
        if self.mUseDuration:
            other = Period(start=self.mStart.duplicate(), duration=self.mDuration.duplicate())
        else:
            other = Period(start=self.mStart.duplicate(), end=self.mEnd.duplicate())
        return other


    def __hash__(self):
        return hash((self.mStart, self.getEnd(),))


    def __repr__(self):
        return "Period %s" % (self.getText(),)


    def __str__(self):
        return self.getText()


    def __eq__(self, comp):
        return self.mStart == comp.mStart and self.getEnd() == comp.getEnd()


    def __gt__(self, comp):
        return self.mStart > comp


    def __lt__(self, comp):
        return self.mStart < comp.mStart  \
            or (self.mStart == comp.mStart) and self.getEnd() < comp.getEnd()


    @classmethod
    def parseText(cls, data):
        period = cls()
        period.parse(data)
        return period


    def parse(self, data, fullISO=False):
        try:
            splits = data.split('/', 1)
            if len(splits) == 2:
                start = splits[0]
                end = splits[1]

                self.mStart.parse(start, fullISO)
                if end[0] == 'P':
                    self.mDuration = Duration.parseText(end)
                    self.mUseDuration = True
                    self.mEnd = None
                else:
                    self.mEnd.parse(end, fullISO)
                    self.mUseDuration = False
                    self.mDuration = None
            else:
                raise ValueError
        except IndexError:
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
        start = XML.SubElement(node, xmlutils.makeTag(namespace, xmldefinitions.period_start))
        start.text = self.mStart.getXMLText()

        if self.mUseDuration:
            duration = XML.SubElement(node, xmlutils.makeTag(namespace, xmldefinitions.period_duration))
            duration.text = self.mDuration.getText()
        else:
            end = XML.SubElement(node, xmlutils.makeTag(namespace, xmldefinitions.period_end))
            end.text = self.mEnd.getXMLText()


    def parseJSON(self, jobject):
        """
        jCal encodes this as an array of two values. We convert back into a single "/"
        separated string and parse as normal.
        """
        self.parse("%s/%s" % tuple(jobject), True)


    def writeJSON(self, jobject):
        """
        jCal encodes this value as an array with two components.
        """
        value = [self.mStart.getXMLText(), ]
        if self.mUseDuration:
            value.append(self.mDuration.getText())
        else:
            value.append(self.mEnd.getXMLText())
        jobject.append(value)


    def getStart(self):
        return self.mStart


    def getEnd(self):
        if self.mEnd is None:
            self.mEnd = self.mStart + self.mDuration
        return self.mEnd


    def getDuration(self):
        if self.mDuration is None:
            self.mDuration = self.mEnd - self.mStart
        return self.mDuration


    def getUseDuration(self):
        return self.mUseDuration


    def setUseDuration(self, use):
        self.mUseDuration = use
        if self.mUseDuration and self.mDuration is None:
            self.getDuration()
        elif not self.mUseDuration and self.mEnd is None:
            self.getEnd()


    def isDateWithinPeriod(self, dt):
        # Inclusive start, exclusive end
        return dt >= self.mStart and dt < self.getEnd()


    def isDateBeforePeriod(self, dt):
        # Inclusive start
        return dt < self.mStart


    def isDateAfterPeriod(self, dt):
        # Exclusive end
        return dt >= self.getEnd()


    def isPeriodOverlap(self, p):
        # Inclusive start, exclusive end
        return not (self.mStart >= p.getEnd() or self.getEnd() <= p.mStart)


    def adjustToUTC(self):
        self.mStart.adjustToUTC()
        self.getEnd().adjustToUTC()


    def describeDuration(self):
        return ""
