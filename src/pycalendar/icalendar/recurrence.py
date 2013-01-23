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

from pycalendar import xmlutils
from pycalendar.datetime import DateTime
from pycalendar.icalendar import definitions, xmldefinitions
from pycalendar.period import Period
from pycalendar.valueutils import ValueMixin
import cStringIO as StringIO
import xml.etree.cElementTree as XML

def WeekDayNumCompare_compare(w1, w2):

    if w1[0] < w2[0]:
        return -1
    elif w1[0] > w2[0]:
        return 1
    elif w1[1] < w2[1]:
        return -1
    elif w1[1] > w2[1]:
        return 1
    else:
        return 0



def WeekDayNumSort_less_than(w1, w2):

    return (w1[0] < w2[0]) or (w1[0] == w2[0]) and (w1[1] < w2[1])



class Recurrence(ValueMixin):

    cFreqMap = {
        definitions.cICalValue_RECUR_SECONDLY : definitions.eRecurrence_SECONDLY,
        definitions.cICalValue_RECUR_MINUTELY : definitions.eRecurrence_MINUTELY,
        definitions.cICalValue_RECUR_HOURLY   : definitions.eRecurrence_HOURLY,
        definitions.cICalValue_RECUR_DAILY    : definitions.eRecurrence_DAILY,
        definitions.cICalValue_RECUR_WEEKLY   : definitions.eRecurrence_WEEKLY,
        definitions.cICalValue_RECUR_MONTHLY  : definitions.eRecurrence_MONTHLY,
        definitions.cICalValue_RECUR_YEARLY   : definitions.eRecurrence_YEARLY,
    }

    cFreqToXMLMap = {
        definitions.eRecurrence_SECONDLY: xmldefinitions.recur_freq_secondly,
        definitions.eRecurrence_MINUTELY: xmldefinitions.recur_freq_minutely,
        definitions.eRecurrence_HOURLY: xmldefinitions.recur_freq_hourly,
        definitions.eRecurrence_DAILY: xmldefinitions.recur_freq_daily,
        definitions.eRecurrence_WEEKLY: xmldefinitions.recur_freq_weekly,
        definitions.eRecurrence_MONTHLY: xmldefinitions.recur_freq_monthly,
        definitions.eRecurrence_YEARLY: xmldefinitions.recur_freq_yearly,
    }

    cRecurMap = {
        definitions.cICalValue_RECUR_FREQ       : definitions.eRecurrence_FREQ,
        definitions.cICalValue_RECUR_UNTIL      : definitions.eRecurrence_UNTIL,
        definitions.cICalValue_RECUR_COUNT      : definitions.eRecurrence_COUNT,
        definitions.cICalValue_RECUR_INTERVAL   : definitions.eRecurrence_INTERVAL,
        definitions.cICalValue_RECUR_BYSECOND   : definitions.eRecurrence_BYSECOND,
        definitions.cICalValue_RECUR_BYMINUTE   : definitions.eRecurrence_BYMINUTE,
        definitions.cICalValue_RECUR_BYHOUR     : definitions.eRecurrence_BYHOUR,
        definitions.cICalValue_RECUR_BYDAY      : definitions.eRecurrence_BYDAY,
        definitions.cICalValue_RECUR_BYMONTHDAY : definitions.eRecurrence_BYMONTHDAY,
        definitions.cICalValue_RECUR_BYYEARDAY  : definitions.eRecurrence_BYYEARDAY,
        definitions.cICalValue_RECUR_BYWEEKNO   : definitions.eRecurrence_BYWEEKNO,
        definitions.cICalValue_RECUR_BYMONTH    : definitions.eRecurrence_BYMONTH,
        definitions.cICalValue_RECUR_BYSETPOS   : definitions.eRecurrence_BYSETPOS,
        definitions.cICalValue_RECUR_WKST       : definitions.eRecurrence_WKST,
    }

    cWeekdayMap = {
        definitions.cICalValue_RECUR_WEEKDAY_SU : definitions.eRecurrence_WEEKDAY_SU,
        definitions.cICalValue_RECUR_WEEKDAY_MO : definitions.eRecurrence_WEEKDAY_MO,
        definitions.cICalValue_RECUR_WEEKDAY_TU : definitions.eRecurrence_WEEKDAY_TU,
        definitions.cICalValue_RECUR_WEEKDAY_WE : definitions.eRecurrence_WEEKDAY_WE,
        definitions.cICalValue_RECUR_WEEKDAY_TH : definitions.eRecurrence_WEEKDAY_TH,
        definitions.cICalValue_RECUR_WEEKDAY_FR : definitions.eRecurrence_WEEKDAY_FR,
        definitions.cICalValue_RECUR_WEEKDAY_SA : definitions.eRecurrence_WEEKDAY_SA,
    }

    cWeekdayRecurMap = dict([(v, k) for k, v in cWeekdayMap.items()])

    cUnknownIndex = -1

    def __init__(self):
        self.init_Recurrence()


    def duplicate(self):
        other = Recurrence()

        other.mFreq = self.mFreq

        other.mUseCount = self.mUseCount
        other.mCount = self.mCount
        other.mUseUntil = self.mUseUntil
        if other.mUseUntil:
            other.mUntil = self.mUntil.duplicate()

        other.mInterval = self.mInterval
        if self.mBySeconds is not None:
            other.mBySeconds = self.mBySeconds[:]
        if self.mByMinutes is not None:
            other.mByMinutes = self.mByMinutes[:]
        if self.mByHours is not None:
            other.mByHours = self.mByHours[:]
        if self.mByDay is not None:
            other.mByDay = self.mByDay[:]
        if self.mByMonthDay is not None:
            other.mByMonthDay = self.mByMonthDay[:]
        if self.mByYearDay is not None:
            other.mByYearDay = self.mByYearDay[:]
        if self.mByWeekNo is not None:
            other.mByWeekNo = self.mByWeekNo[:]
        if self.mByMonth is not None:
            other.mByMonth = self.mByMonth[:]
        if self.mBySetPos is not None:
            other.mBySetPos = self.mBySetPos[:]
        other.mWeekstart = self.mWeekstart

        other.mCached = self.mCached
        if self.mCacheStart:
            other.mCacheStart = self.mCacheStart.duplicate()
        if self.mCacheUpto:
            other.mCacheUpto = self.mCacheUpto.duplicate()
        other.mFullyCached = self.mFullyCached
        if self.mRecurrences:
            other.mRecurrences = self.mRecurrences[:]

        return other


    def init_Recurrence(self):
        self.mFreq = definitions.eRecurrence_YEARLY

        self.mUseCount = False
        self.mCount = 0

        self.mUseUntil = False
        self.mUntil = None

        self.mInterval = 1
        self.mBySeconds = None
        self.mByMinutes = None
        self.mByHours = None
        self.mByDay = None
        self.mByMonthDay = None
        self.mByYearDay = None
        self.mByWeekNo = None
        self.mByMonth = None
        self.mBySetPos = None
        self.mWeekstart = definitions.eRecurrence_WEEKDAY_MO

        self.mCached = False
        self.mCacheStart = None
        self.mCacheUpto = None
        self.mFullyCached = False
        self.mRecurrences = None


    def __hash__(self):
        return hash((
            self.mFreq,
            self.mUseCount,
            self.mCount,
            self.mUseUntil,
            self.mUntil,
            self.mInterval,
            tuple(self.mBySeconds) if self.mBySeconds else None,
            tuple(self.mByMinutes) if self.mByMinutes else None,
            tuple(self.mByHours) if self.mByHours else None,
            tuple(self.mByDay) if self.mByDay else None,
            tuple(self.mByMonthDay) if self.mByMonthDay else None,
            tuple(self.mByYearDay) if self.mByYearDay else None,
            tuple(self.mByWeekNo) if self.mByWeekNo else None,
            tuple(self.mByMonth) if self.mByMonth else None,
            tuple(self.mBySetPos) if self.mBySetPos else None,
            self.mWeekstart,
        ))


    def __ne__(self, other):
        return not self.__eq__(other)


    def __eq__(self, other):
        if not isinstance(other, Recurrence):
            return False
        return self.equals(other)


    def equals(self, comp):
        return (self.mFreq == comp.mFreq) \
                and (self.mUseCount == comp.mUseCount) and (self.mCount == comp.mCount) \
                and (self.mUseUntil == comp.mUseUntil) and (self.mUntil == comp.mUntil) \
                and (self.mInterval == comp.mInterval) \
                and self.equalsNum(self.mBySeconds, comp.mBySeconds) \
                and self.equalsNum(self.mByMinutes, comp.mByMinutes) \
                and self.equalsNum(self.mByHours, comp.mByHours) \
                and self.equalsDayNum(self.mByDay, comp.mByDay) \
                and self.equalsNum(self.mByMonthDay, comp.mByMonthDay) \
                and self.equalsNum(self.mByYearDay, comp.mByYearDay) \
                and self.equalsNum(self.mByWeekNo, comp.mByWeekNo) \
                and self.equalsNum(self.mByMonth, comp.mByMonth) \
                and self.equalsNum(self.mBySetPos, comp.mBySetPos) \
                and (self.mWeekstart == comp.mWeekstart)


    def equalsNum(self, items1, items2):
        # Check sizes first
        if items1 is None:
            items1 = []
        if items2 is None:
            items2 = []
        if len(items1) != len(items2):
            return False
        elif len(items1) == 0:
            return True

        # Copy and sort each one for comparison
        temp1 = items1[:]
        temp2 = items2[:]
        temp1.sort()
        temp2.sort()

        for i in range(0, len(temp1)):
            if temp1[i] != temp2[i]:
                return False
        return True


    def equalsDayNum(self, items1, items2):
        # Check sizes first
        if items1 is None:
            items1 = []
        if items2 is None:
            items2 = []
        if len(items1) != len(items2):
            return False
        elif len(items1) == 0:
            return True

        # Copy and sort each one for comparison
        temp1 = items1[:]
        temp2 = items2[:]
        temp1.sort()
        temp2.sort()

        for i in range(0, len(temp1)):
            if temp1[i] != temp2[i]:
                return False
        return True


    def getFreq(self):
        return self.mFreq


    def setFreq(self, freq):
        self.mFreq = freq


    def getUseUntil(self):
        return self.mUseUntil


    def setUseUntil(self, use_until):
        self.mUseUntil = use_until


    def getUntil(self):
        return self.mUntil


    def setUntil(self, until):
        self.mUntil = until


    def getUseCount(self):
        return self.mUseCount


    def setUseCount(self, use_count):
        self.mUseCount = use_count


    def getCount(self):
        return self.mCount


    def setCount(self, count):
        self.mCount = count


    def getInterval(self):
        return self.mInterval


    def setInterval(self, interval):
        self.mInterval = interval


    def getByMonth(self):
        return self.mByMonth


    def setByMonth(self, by):
        self.mByMonth = by[:]


    def getByMonthDay(self):
        return self.mByMonthDay


    def setByMonthDay(self, by):
        self.mByMonthDay = by[:]


    def getByYearDay(self):
        return self.mByYearDay


    def setByYearDay(self, by):
        self.mByYearDay = by[:]


    def getByDay(self):
        return self.mByDay


    def setByDay(self, by):
        self.mByDay = by[:]


    def getBySetPos(self):
        return self.mBySetPos


    def setBySetPos(self, by):
        self.mBySetPos = by


    def parse(self, data):
        self.init_Recurrence()

        # Tokenise using ''
        tokens = data.split(";")
        tokens.reverse()

        if len(tokens) == 0:
            raise ValueError("Recurrence: Invalid recurrence rule value")

        while len(tokens) != 0:
            # Get next token
            token = tokens.pop()
            try:
                tname, tvalue = token.split("=")
            except ValueError:
                raise ValueError("Recurrence: Invalid token '%s'" % (token,))

            # Determine token type
            index = Recurrence.cRecurMap.get(tname, Recurrence.cUnknownIndex)
            if index == Recurrence.cUnknownIndex:
                raise ValueError("Recurrence: Invalid token '%s'" % (tname,))

            # Parse remainder based on index
            if index == definitions.eRecurrence_FREQ:
                # Get the FREQ value
                index = Recurrence.cFreqMap.get(tvalue, Recurrence.cUnknownIndex)
                if index == Recurrence.cUnknownIndex:
                    raise ValueError("Recurrence: Invalid FREQ value")
                self.mFreq = index

            elif index == definitions.eRecurrence_UNTIL:
                if self.mUseCount:
                    raise ValueError("Recurrence: Can't have both UNTIL and COUNT")
                self.mUseUntil = True
                if self.mUntil is None:
                    self.mUntil = DateTime()
                try:
                    self.mUntil.parse(tvalue)
                except ValueError:
                    raise ValueError("Recurrence: Invalid UNTIL value")

            elif index == definitions.eRecurrence_COUNT:
                if self.mUseUntil:
                    raise ValueError("Recurrence: Can't have both UNTIL and COUNT")
                self.mUseCount = True
                try:
                    self.mCount = int(tvalue)
                except ValueError:
                    raise ValueError("Recurrence: Invalid COUNT value")

                # Must not be less than one
                if self.mCount < 1:
                    raise ValueError("Recurrence: Invalid COUNT value")

            elif index == definitions.eRecurrence_INTERVAL:
                try:
                    self.mInterval = int(tvalue)
                except ValueError:
                    raise ValueError("Recurrence: Invalid INTERVAL value")

                # Must NOT be less than one
                if self.mInterval < 1:
                    raise ValueError("Recurrence: Invalid INTERVAL value")

            elif index == definitions.eRecurrence_BYSECOND:
                if self.mBySeconds is not None:
                    raise ValueError("Recurrence: Only one BYSECOND allowed")
                self.mBySeconds = []
                self.parseList(tvalue, self.mBySeconds, 0, 60, errmsg="Recurrence: Invalid BYSECOND value")

            elif index == definitions.eRecurrence_BYMINUTE:
                if self.mByMinutes is not None:
                    raise ValueError("Recurrence: Only one BYMINUTE allowed")
                self.mByMinutes = []
                self.parseList(tvalue, self.mByMinutes, 0, 59, errmsg="Recurrence: Invalid BYMINUTE value")

            elif index == definitions.eRecurrence_BYHOUR:
                if self.mByHours is not None:
                    raise ValueError("Recurrence: Only one BYHOUR allowed")
                self.mByHours = []
                self.parseList(tvalue, self.mByHours, 0, 23, errmsg="Recurrence: Invalid BYHOUR value")

            elif index == definitions.eRecurrence_BYDAY:
                if self.mByDay is not None:
                    raise ValueError("Recurrence: Only one BYDAY allowed")
                self.mByDay = []
                self.parseListDW(tvalue, self.mByDay, errmsg="Recurrence: Invalid BYDAY value")

            elif index == definitions.eRecurrence_BYMONTHDAY:
                if self.mByMonthDay is not None:
                    raise ValueError("Recurrence: Only one BYMONTHDAY allowed")
                self.mByMonthDay = []
                self.parseList(tvalue, self.mByMonthDay, 1, 31, True, errmsg="Recurrence: Invalid BYMONTHDAY value")

            elif index == definitions.eRecurrence_BYYEARDAY:
                if self.mByYearDay is not None:
                    raise ValueError("Recurrence: Only one BYYEARDAY allowed")
                self.mByYearDay = []
                self.parseList(tvalue, self.mByYearDay, 1, 366, True, errmsg="Recurrence: Invalid BYYEARDAY value")

            elif index == definitions.eRecurrence_BYWEEKNO:
                if self.mByWeekNo is not None:
                    raise ValueError("Recurrence: Only one BYWEEKNO allowed")
                self.mByWeekNo = []
                self.parseList(tvalue, self.mByWeekNo, 1, 53, True, errmsg="Recurrence: Invalid BYWEEKNO value")

            elif index == definitions.eRecurrence_BYMONTH:
                if self.mByMonth is not None:
                    raise ValueError("Recurrence: Only one BYMONTH allowed")
                self.mByMonth = []
                self.parseList(tvalue, self.mByMonth, 1, 12, errmsg="Recurrence: Invalid BYMONTH value")

            elif index == definitions.eRecurrence_BYSETPOS:
                if self.mBySetPos is not None:
                    raise ValueError("Recurrence: Only one BYSETPOS allowed")
                self.mBySetPos = []
                self.parseList(tvalue, self.mBySetPos, allowNegative=True, errmsg="Recurrence: Invalid BYSETPOS value")

            elif index == definitions.eRecurrence_WKST:
                index = Recurrence.cWeekdayMap.get(tvalue, Recurrence.cUnknownIndex)
                if (index == Recurrence.cUnknownIndex):
                    raise ValueError("Recurrence: Invalid WKST value")
                self.mWeekstart = index


    def parseList(self, txt, list, min=None, max=None, allowNegative=False, errmsg=""):

        if "," in txt:
            tokens = txt.split(",")
        else:
            tokens = (txt,)

        for token in tokens:
            value = int(token)
            if not allowNegative and value < 0:
                raise ValueError(errmsg)
            avalue = abs(value)
            if min is not None and avalue < min:
                raise ValueError(errmsg)
            if max is not None  and avalue > max:
                raise ValueError(errmsg)
            list.append(value)


    def parseListDW(self, txt, list, errmsg=""):

        if "," in txt:
            tokens = txt.split(",")
        else:
            tokens = (txt,)

        for token in tokens:
            # Get number if present
            num = 0
            if (len(token) > 0) and token[0] in "+-1234567890":
                offset = 0
                while (offset < len(token)) and token[offset] in "+-1234567890":
                    offset += 1

                num = int(token[0:offset])
                token = token[offset:]

                anum = abs(num)
                if anum < 1:
                    raise ValueError(errmsg)
                if anum > 53:
                    raise ValueError(errmsg)

            # Get day
            index = Recurrence.cWeekdayMap.get(token, Recurrence.cUnknownIndex)
            if (index == Recurrence.cUnknownIndex):
                raise ValueError(errmsg)
            wday = index

            list.append((num, wday))


    def generate(self, os):
        try:
            os.write(definitions.cICalValue_RECUR_FREQ)
            os.write("=")

            if self.mFreq == definitions.eRecurrence_SECONDLY:
                os.write(definitions.cICalValue_RECUR_SECONDLY)

            elif self.mFreq == definitions.eRecurrence_MINUTELY:
                os.write(definitions.cICalValue_RECUR_MINUTELY)

            elif self.mFreq == definitions.eRecurrence_HOURLY:
                os.write(definitions.cICalValue_RECUR_HOURLY)

            elif self.mFreq == definitions.eRecurrence_DAILY:
                os.write(definitions.cICalValue_RECUR_DAILY)

            elif self.mFreq == definitions.eRecurrence_WEEKLY:
                os.write(definitions.cICalValue_RECUR_WEEKLY)

            elif self.mFreq == definitions.eRecurrence_MONTHLY:
                os.write(definitions.cICalValue_RECUR_MONTHLY)

            elif self.mFreq == definitions.eRecurrence_YEARLY:
                os.write(definitions.cICalValue_RECUR_YEARLY)

            if self.mUseCount:
                os.write(";")
                os.write(definitions.cICalValue_RECUR_COUNT)
                os.write("=")
                os.write(str(self.mCount))
            elif self.mUseUntil:
                os.write(";")
                os.write(definitions.cICalValue_RECUR_UNTIL)
                os.write("=")
                self.mUntil.generate(os)

            if self.mInterval > 1:
                os.write(";")
                os.write(definitions.cICalValue_RECUR_INTERVAL)
                os.write("=")
                os.write(str(self.mInterval))

            self.generateList(os, definitions.cICalValue_RECUR_BYSECOND, self.mBySeconds)
            self.generateList(os, definitions.cICalValue_RECUR_BYMINUTE, self.mByMinutes)
            self.generateList(os, definitions.cICalValue_RECUR_BYHOUR, self.mByHours)

            if (self.mByDay is not None) and (len(self.mByDay) != 0):
                os.write(";")
                os.write(definitions.cICalValue_RECUR_BYDAY)
                os.write("=")
                comma = False
                for iter in self.mByDay:
                    if comma:
                        os.write(",")
                    comma = True

                    if iter[0] != 0:
                        os.write(str(iter[0]))

                    if iter[1] == definitions.eRecurrence_WEEKDAY_SU:
                        os.write(definitions.cICalValue_RECUR_WEEKDAY_SU)

                    elif iter[1] == definitions.eRecurrence_WEEKDAY_MO:
                        os.write(definitions.cICalValue_RECUR_WEEKDAY_MO)

                    elif iter[1] == definitions.eRecurrence_WEEKDAY_TU:
                        os.write(definitions.cICalValue_RECUR_WEEKDAY_TU)

                    elif iter[1] == definitions.eRecurrence_WEEKDAY_WE:
                        os.write(definitions.cICalValue_RECUR_WEEKDAY_WE)

                    elif iter[1] == definitions.eRecurrence_WEEKDAY_TH:
                        os.write(definitions.cICalValue_RECUR_WEEKDAY_TH)

                    elif iter[1] == definitions.eRecurrence_WEEKDAY_FR:
                        os.write(definitions.cICalValue_RECUR_WEEKDAY_FR)

                    elif iter[1] == definitions.eRecurrence_WEEKDAY_SA:
                        os.write(definitions.cICalValue_RECUR_WEEKDAY_SA)

            self.generateList(os, definitions.cICalValue_RECUR_BYMONTHDAY, self.mByMonthDay)
            self.generateList(os, definitions.cICalValue_RECUR_BYYEARDAY, self.mByYearDay)
            self.generateList(os, definitions.cICalValue_RECUR_BYWEEKNO, self.mByWeekNo)
            self.generateList(os, definitions.cICalValue_RECUR_BYMONTH, self.mByMonth)
            self.generateList(os, definitions.cICalValue_RECUR_BYSETPOS, self.mBySetPos)

            # MO is the default so we do not need it
            if self.mWeekstart != definitions.eRecurrence_WEEKDAY_MO:
                os.write(";")
                os.write(definitions.cICalValue_RECUR_WKST)
                os.write("=")

                if self.mWeekstart == definitions.eRecurrence_WEEKDAY_SU:
                    os.write(definitions.cICalValue_RECUR_WEEKDAY_SU)

                elif self.mWeekstart == definitions.eRecurrence_WEEKDAY_MO:
                    os.write(definitions.cICalValue_RECUR_WEEKDAY_MO)

                elif self.mWeekstart == definitions.eRecurrence_WEEKDAY_TU:
                    os.write(definitions.cICalValue_RECUR_WEEKDAY_TU)

                elif self.mWeekstart == definitions.eRecurrence_WEEKDAY_WE:
                    os.write(definitions.cICalValue_RECUR_WEEKDAY_WE)

                elif self.mWeekstart == definitions.eRecurrence_WEEKDAY_TH:
                    os.write(definitions.cICalValue_RECUR_WEEKDAY_TH)

                elif self.mWeekstart == definitions.eRecurrence_WEEKDAY_FR:
                    os.write(definitions.cICalValue_RECUR_WEEKDAY_FR)

                elif self.mWeekstart == definitions.eRecurrence_WEEKDAY_SA:
                    os.write(definitions.cICalValue_RECUR_WEEKDAY_SA)

        except:
            pass


    def generateList(self, os, title, items):

        if (items is not None) and (len(items) != 0):
            os.write(";")
            os.write(title)
            os.write("=")
            comma = False
            for e in items:
                if comma:
                    os.write(",")
                comma = True
                os.write(str(e))


    def writeXML(self, node, namespace):

        recur = XML.SubElement(node, xmlutils.makeTag(namespace, xmldefinitions.value_recur))

        freq = XML.SubElement(recur, xmlutils.makeTag(namespace, xmldefinitions.recur_freq))
        freq.text = self.cFreqToXMLMap[self.mFreq]

        if self.mUseCount:
            count = XML.SubElement(recur, xmlutils.makeTag(namespace, xmldefinitions.recur_count))
            count.text = str(self.mCount)
        elif self.mUseUntil:
            until = XML.SubElement(recur, xmlutils.makeTag(namespace, xmldefinitions.recur_until))
            self.mUntil.writeXML(until, namespace)

        if self.mInterval > 1:
            interval = XML.SubElement(recur, xmlutils.makeTag(namespace, xmldefinitions.recur_interval))
            interval.text = str(self.mInterval)

        self.writeXMLList(recur, namespace, xmldefinitions.recur_bysecond, self.mBySeconds)
        self.writeXMLList(recur, namespace, xmldefinitions.recur_byminute, self.mByMinutes)
        self.writeXMLList(recur, namespace, xmldefinitions.recur_byhour, self.mByHours)

        if self.mByDay is not None and len(self.mByDay) != 0:
            for iter in self.mByDay:
                byday = XML.SubElement(recur, xmlutils.makeTag(namespace, xmldefinitions.recur_byday))
                data = ""
                if iter[0] != 0:
                    data = str(iter[0])
                data += self.cWeekdayRecurMap.get(iter[1], "")
                byday.text = data

        self.writeXMLList(recur, namespace, xmldefinitions.recur_bymonthday, self.mByMonthDay)
        self.writeXMLList(recur, namespace, xmldefinitions.recur_byyearday, self.mByYearDay)
        self.writeXMLList(recur, namespace, xmldefinitions.recur_byweekno, self.mByWeekNo)
        self.writeXMLList(recur, namespace, xmldefinitions.recur_bymonth, self.mByMonth)
        self.writeXMLList(recur, namespace, xmldefinitions.recur_bysetpos, self.mBySetPos)

        # MO is the default so we do not need it
        if self.mWeekstart != definitions.eRecurrence_WEEKDAY_MO:
            wkst = XML.SubElement(recur, xmlutils.makeTag(namespace, xmldefinitions.recur_wkst))
            wkst.text = self.cWeekdayRecurMap.get(self.mWeekstart, definitions.cICalValue_RECUR_WEEKDAY_MO)


    def writeXMLList(self, node, namespace, name, items):
        if items is not None and len(items) != 0:
            for item in items:
                child = XML.SubElement(node, xmlutils.makeTag(namespace, name))
                child.text = str(item)


    def parseJSON(self, jobject):
        self.parse(str(jobject))


    def writeJSON(self, jobject):
        jobject.append(self.getText())


    def hasBy(self):
        return (self.mBySeconds is not None) and (len(self.mBySeconds) != 0) \
                or (self.mByMinutes is not None) and (len(self.mByMinutes) != 0) \
                or (self.mByHours is not None) and (len(self.mByHours) != 0) \
                or (self.mByDay is not None) and (len(self.mByDay) != 0) \
                or (self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0) \
                or (self.mByYearDay is not None) and (len(self.mByYearDay) != 0) \
                or (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0) \
                or (self.mByMonth is not None) and (len(self.mByMonth) != 0) \
                or (self.mBySetPos is not None) and (len(self.mBySetPos) != 0)


    def isSimpleRule(self):
        # One that has no BYxxx rules
        return not self.hasBy()


    def isAdvancedRule(self):
        # One that has BYMONTH,
        # BYMONTHDAY (with no negative value),
        # BYDAY (with multiple unumbered, or numbered with all the same number
        # (1..4, -2, -1)
        # BYSETPOS with +1, or -1 only
        # no others

        # First checks the ones we do not handle at all
        if ((self.mBySeconds is not None) and (len(self.mBySeconds) != 0) \
                or (self.mByMinutes is not None) and (len(self.mByMinutes) != 0) \
                or (self.mByHours is not None) and (len(self.mByHours) != 0) \
                or (self.mByYearDay is not None) and (len(self.mByYearDay) != 0) \
                or (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0)):
            return False

        # Check BYMONTHDAY numbers (we can handle -7...-1, 1..31)
        if self.mByMonthDay is not None:
            for iter in self.mByMonthDay:
                if (iter < -7) or (iter > 31) or (iter == 0):
                    return False

        # Check BYDAY numbers
        if self.mByDay is not None:
            number = 0
            first = True
            for iter in self.mByDay:

                # Get the first number
                if (first):
                    number = iter[0]
                    first = False

                    # Check number range
                    if (number > 4) or (number < -2):
                        return False

                # If current differs from last, then we have an error
                elif number != iter[0]:
                    return False

        # Check BYSETPOS numbers
        if self.mBySetPos is not None:
            if len(self.mBySetPos) > 1:
                return False
            if (len(self.mBySetPos) == 1) and (self.mBySetPos[0] != -1) and (self.mBySetPos[0] != 1):
                return False

        # If we get here it must be OK
        return True


    def getUIDescription(self):
        try:
            # For now just use iCal item
            sout = StringIO()
            self.generate(sout)
            result = sout.getvalue()
        except:
            result = ""

        return result


    def expand(self, start, range, items, float_offset=0):

        # Must have recurrence list at this point
        if self.mRecurrences is None:
            self.mRecurrences = []

        # Wipe cache if start is different
        if self.mCached and (start != self.mCacheStart):
            self.mCached = False
            self.mFullyCached = False
            self.mRecurrences = []

        # Is the current cache complete or does it extend past the requested
        # range end
        if not self.mCached or not self.mFullyCached \
                and (self.mCacheUpto is None or self.mCacheUpto < range.getEnd()):
            cache_range = range.duplicate()

            # If partially cached just cache from previous cache end up to new
            # end
            if self.mCached:
                cache_range = Period(self.mCacheUpto, range.getEnd())

            # Simple expansion is one where there is no BYXXX rule part
            if not self.hasBy():
                self.mFullyCached = self.simpleExpand(start, cache_range, self.mRecurrences, float_offset)
            else:
                self.mFullyCached = self.complexExpand(start, cache_range, self.mRecurrences, float_offset)

            # Set cache values
            self.mCached = True
            self.mCacheStart = start
            self.mCacheUpto = range.getEnd()

        # Just return the cached items in the requested range
        limited = not self.mFullyCached
        for iter in self.mRecurrences:
            if range.isDateWithinPeriod(iter):
                items.append(iter)
            else:
                limited = True
        return limited


    def simpleExpand(self, start, range, items, float_offset):
        start_iter = start.duplicate()
        ctr = 0

        if self.mUseUntil:
            float_until = self.mUntil.duplicate()
            if start.floating():
                float_until.setTimezoneID(0)
                float_until.offsetSeconds(float_offset)

        while True:
            # Exit if after period we want
            if range.isDateAfterPeriod(start_iter):
                return False

            # Add current one to list
            items.append(start_iter.duplicate())

            # Get next item
            start_iter.recur(self.mFreq, self.mInterval)

            # Check limits
            if self.mUseCount:
                # Bump counter and exit if over
                ctr += 1
                if ctr >= self.mCount:
                    return True
            elif self.mUseUntil:
                # Exit if next item is after until (its OK if its the same as
                # UNTIL as UNTIL is inclusive)
                if start_iter > float_until:
                    return True


    def complexExpand(self, start, range, items, float_offset):
        start_iter = start.duplicate()
        ctr = 0

        if self.mUseUntil:
            float_until = self.mUntil.duplicate()
            if start.floating():
                float_until.setTimezoneID(None)
                float_until.offsetSeconds(float_offset)

        # Always add the initial instance DTSTART
        items.append(start.duplicate())
        if self.mUseCount:
            # Bump counter and exit if over
            ctr += 1
            if ctr >= self.mCount:
                return True

        # Need to re-initialise start based on BYxxx rules
        while True:
            # Behaviour is based on frequency
            set_items = []

            if self.mFreq == definitions.eRecurrence_SECONDLY:
                self.generateSecondlySet(start_iter, set_items)

            elif self.mFreq == definitions.eRecurrence_MINUTELY:
                self.generateMinutelySet(start_iter, set_items)

            elif self.mFreq == definitions.eRecurrence_HOURLY:
                self.generateHourlySet(start_iter, set_items)

            elif self.mFreq == definitions.eRecurrence_DAILY:
                self.generateDailySet(start_iter, set_items)

            elif self.mFreq == definitions.eRecurrence_WEEKLY:
                self.generateWeeklySet(start_iter, set_items)

            elif self.mFreq == definitions.eRecurrence_MONTHLY:
                self.generateMonthlySet(start_iter, set_items)

            elif self.mFreq == definitions.eRecurrence_YEARLY:
                self.generateYearlySet(start_iter, set_items)

            # Always sort the set as BYxxx rules may not be sorted
            #set_items.sort(cmp=DateTime.sort)
            set_items.sort(key=lambda x: x.getPosixTime())

            # Process each one in the generated set
            for iter in set_items:

                # Ignore if it is before the actual start - we need this
                # because the expansion
                # can go back in time from the real start, but we must exclude
                # those when counting
                # even if they are not within the requested range
                if iter < start:
                    continue

                # Exit if after period we want
                if range.isDateAfterPeriod(iter):
                    return False

                # Exit if beyond the UNTIL limit
                if self.mUseUntil:
                    # Exit if next item is after until (its OK if its the same
                    # as UNTIL as UNTIL is inclusive)
                    if iter > float_until:
                        return True

                # Special for start instance
                if (ctr == 1) and (start == iter):
                    continue

                # Add current one to list
                items.append(iter)

                # Check limits
                if self.mUseCount:
                    # Bump counter and exit if over
                    ctr += 1
                    if ctr >= self.mCount:
                        return True

            # Exit if after period we want
            if range.isDateAfterPeriod(start_iter):
                return False

            # Get next item
            start_iter.recur(self.mFreq, self.mInterval)


    def clear(self):
        self.mCached = False
        self.mFullyCached = False
        if self.mRecurrences is not None:
            self.mRecurrences = []


    # IMPORTANT ExcludeFutureRecurrence assumes mCacheStart is setup with the
    # owning VEVENT's DTSTART
    # Currently this method is only called when a recurrence is being removed
    # so
    # the recurrence data should be cached

    # Exclude dates on or after the chosen one
    def excludeFutureRecurrence(self, exclude):
        # Expand the rule upto the exclude date
        items = []
        period = Period()
        period.init(self.mCacheStart, exclude)
        self.expand(self.mCacheStart, period, items)

        # Adjust UNTIL or add one if no COUNT
        if self.getUseUntil() or not self.getUseCount():
            # The last one is just less than the exclude date
            if len(items) != 0:
                # Now use the data as the UNTIL
                self.mUseUntil = True
                self.mUntil = items[-1]

        # Adjust COUNT
        elif self.getUseCount():
            # The last one is just less than the exclude date
            self.mUseCount = True
            self.mCount = len(items)

        # Now clear out the cached set after making changes
        self.clear()


    def generateYearlySet(self, start, items):
        # All possible BYxxx are valid, though some combinations are not

        # Start with initial date-time
        items.append(start.duplicate())

        if (self.mByMonth is not None) and (len(self.mByMonth) != 0):
            items[:] = self.byMonthExpand(items)

        if (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0):
            items[:] = self.byWeekNoExpand(items)

        if (self.mByYearDay is not None) and (len(self.mByYearDay) != 0):
            items[:] = self.byYearDayExpand(items)

        if (self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0):
            items[:] = self.byMonthDayExpand(items)

        if (self.mByDay is not None) and (len(self.mByDay) != 0):
            # BYDAY is complicated:
            # if BYDAY is included with BYYEARDAY or BYMONTHDAY then it
            # contracts the recurrence set
            # else it expands it, but the expansion depends on the frequency
            # and other BYxxx periodicities

            if ((self.mByYearDay is not None) and (len(self.mByYearDay) != 0)) \
                    or ((self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0)):
                items[:] = self.byDayLimit(items)
            elif (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0):
                items[:] = self.byDayExpandWeekly(items)
            elif (self.mByMonth is not None) and (len(self.mByMonth) != 0):
                items[:] = self.byDayExpandMonthly(items)
            else:
                items[:] = self.byDayExpandYearly(items)

        if (self.mByHours is not None) and (len(self.mByHours) != 0):
            items[:] = self.byHourExpand(items)

        if (self.mByMinutes is not None) and (len(self.mByMinutes) != 0):
            items[:] = self.byMinuteExpand(items)

        if (self.mBySeconds is not None) and (len(self.mBySeconds) != 0):
            items[:] = self.bySecondExpand(items)

        if (self.mBySetPos is not None) and (len(self.mBySetPos) != 0):
            items[:] = self.bySetPosLimit(items)


    def generateMonthlySet(self, start, items):
        # Cannot have BYYEARDAY and BYWEEKNO

        # Start with initial date-time
        items.append(start.duplicate())

        if (self.mByMonth is not None) and (len(self.mByMonth) != 0):
            # BYMONTH limits the range of possible values
            items[:] = self.byMonthLimit(items)
            if (len(items) == 0):
                return

        # No BYWEEKNO

        # No BYYEARDAY

        if (self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0):
            items[:] = self.byMonthDayExpand(items)

        if (self.mByDay is not None) and (len(self.mByDay) != 0):
            # BYDAY is complicated:
            # if BYDAY is included with BYYEARDAY or BYMONTHDAY then it
            # contracts the recurrence set
            # else it expands it, but the expansion depends on the frequency
            # and other BYxxx periodicities

            if ((self.mByYearDay is not None) and (len(self.mByYearDay) != 0)) \
                    or ((self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0)):
                items[:] = self.byDayLimit(items)
            else:
                items[:] = self.byDayExpandMonthly(items)

        if ((self.mByHours is not None) and (len(self.mByHours) != 0)):
            items[:] = self.byHourExpand(items)

        if ((self.mByMinutes is not None) and (len(self.mByMinutes) != 0)):
            items[:] = self.byMinuteExpand(items)

        if ((self.mBySeconds is not None) and (len(self.mBySeconds) != 0)):
            items[:] = self.bySecondExpand(items)

        if ((self.mBySetPos is not None) and (len(self.mBySetPos) != 0)):
            items[:] = self.bySetPosLimit(items)


    def generateWeeklySet(self, start, items):
        # Cannot have BYYEARDAY and BYMONTHDAY

        # Start with initial date-time
        items.append(start.duplicate())

        if (self.mByMonth is not None) and (len(self.mByMonth) != 0):
            # BYMONTH limits the range of possible values
            items[:] = self.byMonthLimit(items)
            if (len(items) == 0):
                return

        if (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0):
            items[:] = self.byWeekNoLimit(items)
            if (len(items) == 0):
                return

        # No BYYEARDAY

        # No BYMONTHDAY

        if (self.mByDay is not None) and (len(self.mByDay) != 0):
            items[:] = self.byDayExpandWeekly(items)

        if (self.mByHours is not None) and (len(self.mByHours) != 0):
            items[:] = self.byHourExpand(items)

        if (self.mByMinutes is not None) and (len(self.mByMinutes) != 0):
            items[:] = self.byMinuteExpand(items)

        if (self.mBySeconds is not None) and (len(self.mBySeconds) != 0):
            items[:] = self.bySecondExpand(items)

        if (self.mBySetPos is not None) and (len(self.mBySetPos) != 0):
            items[:] = self.bySetPosLimit(items)


    def generateDailySet(self, start, items):
        # Cannot have BYYEARDAY

        # Start with initial date-time
        items.append(start.duplicate())

        if (self.mByMonth is not None) and (len(self.mByMonth) != 0):
            # BYMONTH limits the range of possible values
            items[:] = self.byMonthLimit(items)
            if (len(items) == 0):
                return

        if (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0):
            items[:] = self.byWeekNoLimit(items)
            if (len(items) == 0):
                return

        # No BYYEARDAY

        if (self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0):
            items[:] = self.byMonthDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByDay is not None) and (len(self.mByDay) != 0):
            items[:] = self.byDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByHours is not None) and (len(self.mByHours) != 0):
            items[:] = self.byHourExpand(items)

        if (self.mByMinutes is not None) and (len(self.mByMinutes) != 0):
            items[:] = self.byMinuteExpand(items)

        if (self.mBySeconds is not None) and (len(self.mBySeconds) != 0):
            items[:] = self.bySecondExpand(items)

        if (self.mBySetPos is not None) and (len(self.mBySetPos) != 0):
            items[:] = self.bySetPosLimit(items)


    def generateHourlySet(self, start, items):
        # Cannot have BYYEARDAY

        # Start with initial date-time
        items.append(start.duplicate())

        if (self.mByMonth is not None) and (len(self.mByMonth) != 0):
            # BYMONTH limits the range of possible values
            items[:] = self.byMonthLimit(items)
            if (len(items) == 0):
                return

        if (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0):
            items[:] = self.byWeekNoLimit(items)
            if (len(items) == 0):
                return

        # No BYYEARDAY

        if (self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0):
            items[:] = self.byMonthDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByDay is not None) and (len(self.mByDay) != 0):
            items[:] = self.byDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByHours is not None) and (len(self.mByHours) != 0):
            items[:] = self.byHourLimit(items)
            if (len(items) == 0):
                return

        if (self.mByMinutes is not None) and (len(self.mByMinutes) != 0):
            items[:] = self.byMinuteExpand(items)

        if (self.mBySeconds is not None) and (len(self.mBySeconds) != 0):
            items[:] = self.bySecondExpand(items)

        if (self.mBySetPos is not None) and (len(self.mBySetPos) != 0):
            items[:] = self.bySetPosLimit(items)


    def generateMinutelySet(self, start, items):
        # Cannot have BYYEARDAY

        # Start with initial date-time
        items.append(start.duplicate())

        if (self.mByMonth is not None) and (len(self.mByMonth) != 0):
            # BYMONTH limits the range of possible values
            items[:] = self.byMonthLimit(items)
            if (len(items) == 0):
                return

        if (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0):
            items[:] = self.byWeekNoLimit(items)
            if (len(items) == 0):
                return

        # No BYYEARDAY

        if (self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0):
            items[:] = self.byMonthDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByDay is not None) and (len(self.mByDay) != 0):
            items[:] = self.byDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByHours is not None) and (len(self.mByHours) != 0):
            items[:] = self.byHourLimit(items)
            if (len(items) == 0):
                return

        if (self.mByMinutes is not None) and (len(self.mByMinutes) != 0):
            items[:] = self.byMinuteLimit(items)
            if (len(items) == 0):
                return

        if (self.mBySeconds is not None) and (len(self.mBySeconds) != 0):
            items[:] = self.bySecondExpand(items)

        if (self.mBySetPos is not None) and (len(self.mBySetPos) != 0):
            items[:] = self.bySetPosLimit(items)


    def generateSecondlySet(self, start, items):
        # Cannot have BYYEARDAY

        # Start with initial date-time
        items.append(start.duplicate())

        if (self.mByMonth is not None) and (len(self.mByMonth) != 0):
            # BYMONTH limits the range of possible values
            items[:] = self.byMonthLimit(items)
            if (len(items) == 0):
                return

        if (self.mByWeekNo is not None) and (len(self.mByWeekNo) != 0):
            items[:] = self.byWeekNoLimit(items)
            if (len(items) == 0):
                return

        # No BYYEARDAY

        if (self.mByMonthDay is not None) and (len(self.mByMonthDay) != 0):
            items[:] = self.byMonthDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByDay is not None) and (len(self.mByDay) != 0):
            items[:] = self.byDayLimit(items)
            if (len(items) == 0):
                return

        if (self.mByHours is not None) and (len(self.mByHours) != 0):
            items[:] = self.byHourLimit(items)
            if (len(items) == 0):
                return

        if (self.mByMinutes is not None) and (len(self.mByMinutes) != 0):
            items[:] = self.byMinuteLimit(items)
            if (len(items) == 0):
                return

        if (self.mBySeconds is not None) and (len(self.mBySeconds) != 0):
            items[:] = self.bySecondLimit(items)
            if (len(items) == 0):
                return

        if (self.mBySetPos is not None) and (len(self.mBySetPos) != 0):
            items[:] = self.bySetPosLimit(items)


    def byMonthExpand(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYMONTH and generating a new date-time for it and
            # insert into output
            for iter2 in self.mByMonth:
                temp = iter1.duplicate()
                temp.setMonth(iter2)
                output.append(temp)

        return output


    def byWeekNoExpand(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYWEEKNO and generating a new date-time for it and
            # insert into output
            for iter2 in self.mByWeekNo:
                temp = iter1.duplicate()
                temp.setWeekNo(iter2)
                output.append(temp)

        return output


    def byYearDayExpand(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYYEARDAY and generating a new date-time for it
            # and insert into output
            for iter2 in self.mByYearDay:
                temp = iter1.duplicate()
                temp.setYearDay(iter2)
                output.append(temp)

        return output


    def byMonthDayExpand(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYMONTHDAY and generating a new date-time for it
            # and insert into output
            for iter2 in self.mByMonthDay:
                temp = iter1.duplicate()
                temp.setMonthDay(iter2)
                output.append(temp)

        return output


    def byDayExpandYearly(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYDAY and generating a new date-time for it and
            # insert into output
            for iter2 in self.mByDay:
                # Numeric value means specific instance
                if iter2[0] != 0:
                    temp = iter1.duplicate()
                    temp.setDayOfWeekInYear(iter2[0], iter2[1])
                    output.append(temp)
                else:
                    # Every matching day in the year
                    for  i in range(1, 54):
                        temp = iter1.duplicate()
                        temp.setDayOfWeekInYear(i, iter2[1])
                        if temp.getYear() == (iter1).getYear():
                            output.append(temp)

        return output


    def byDayExpandMonthly(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYDAY and generating a new date-time for it and
            # insert into output
            for iter2 in self.mByDay:
                # Numeric value means specific instance
                if iter2[0] != 0:
                    temp = iter1.duplicate()
                    temp.setDayOfWeekInMonth(iter2[0], iter2[1])
                    output.append(temp)
                else:
                    # Every matching day in the month
                    for i in range(1, 7):
                        temp = iter1.duplicate()
                        temp.setDayOfWeekInMonth(i, iter2[1])
                        if temp.getMonth() == iter1.getMonth():
                            output.append(temp)

        return output


    def byDayExpandWeekly(self, dates):
        # Must take into account the WKST value

        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYDAY and generating a new date-time for it and
            # insert into output
            for iter2 in self.mByDay:
                # Numeric values are meaningless so ignore them
                if iter2[0] == 0:
                    temp = iter1.duplicate()

                    # Determine amount of offset to apply to temp to shift it
                    # to the start of the week (backwards)
                    week_start_offset = self.mWeekstart - temp.getDayOfWeek()
                    if week_start_offset > 0:
                        week_start_offset -= 7

                    # Determine amount of offset from the start of the week to
                    # the day we want (forwards)
                    day_in_week_offset = iter2[1] - self.mWeekstart
                    if day_in_week_offset < 0:
                        day_in_week_offset += 7

                    # Apply offsets
                    temp.offsetDay(week_start_offset + day_in_week_offset)
                    output.append(temp)

        return output


    def byHourExpand(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYHOUR and generating a new date-time for it and
            # insert into output
            for iter2 in self.mByHours:
                temp = iter1.duplicate()
                temp.setHours(iter2)
                output.append(temp)

        return output


    def byMinuteExpand(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYMINUTE and generating a new date-time for it and
            # insert into output
            for iter2 in self.mByMinutes:
                temp = iter1.duplicate()
                temp.setMinutes(iter2)
                output.append(temp)

        return output


    def bySecondExpand(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYSECOND and generating a new date-time for it and
            # insert into output
            for iter2 in self.mBySeconds:
                temp = iter1.duplicate()
                temp.setSeconds(iter2)
                output.append(temp)

        return output


    def byMonthLimit(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYMONTH and indicate keep if input month matches
            keep = False
            for iter2 in self.mByMonth:
                keep = (iter1.getMonth() == iter2)
                if keep:
                    break

            if keep:
                output.append(iter1)

        return output


    def byWeekNoLimit(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYWEEKNO and indicate keep if input month matches
            keep = False
            for iter2 in self.mByWeekNo:
                keep = iter1.isWeekNo(iter2)
                if keep:
                    break

            if keep:
                output.append(iter1)

        return output


    def byMonthDayLimit(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYMONTHDAY and indicate keep if input month
            # matches
            keep = False
            for iter2 in self.mByMonthDay:
                keep = iter1.isMonthDay(iter2)
                if keep:
                    break

            if keep:
                output.append(iter1)

        return output


    def byDayLimit(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYDAY and indicate keep if input month matches
            keep = False
            for iter2 in self.mByDay:
                keep = iter1.isDayOfWeekInMonth(iter2[0], iter2[1])
                if keep:
                    break

            if keep:
                output.append(iter1)

        return output


    def byHourLimit(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYHOUR and indicate keep if input hour matches
            keep = False
            for iter2 in self.mByHours:
                keep = (iter1.getHours() == iter2)
                if keep:
                    break

            if keep:
                output.append(iter1)

        return output


    def byMinuteLimit(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYMINUTE and indicate keep if input minute matches
            keep = False
            for iter2 in self.mByMinutes:
                keep = (iter1.getMinutes() == iter2)
                if keep:
                    break

            if keep:
                output.append(iter1)

        return output


    def bySecondLimit(self, dates):
        # Loop over all input items
        output = []
        for iter1 in dates:
            # Loop over each BYSECOND and indicate keep if input second matches
            keep = False
            for iter2 in self.mBySeconds:
                keep = (iter1.getSeconds() == iter2)
                if keep:
                    break

            if keep:
                output.append(iter1)

        return output


    def bySetPosLimit(self, dates):
        # The input dates MUST be sorted in order for this to work properly
        #dates.sort(cmp=DateTime.sort)
        dates.sort(key=lambda x: x.getPosixTime())

        # Loop over each BYSETPOS and extract the relevant component from the
        # input array and add to the output
        output = []
        input_size = len(dates)
        for iter in self.mBySetPos:
            if iter > 0:
                # Positive values are offset from the start
                if iter <= input_size:
                    output.append(dates[iter - 1])
            elif iter < 0:
                # Negative values are offset from the end
                if -iter <= input_size:
                    output.append(dates[input_size + iter])

        return output
