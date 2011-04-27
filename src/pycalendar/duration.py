##
#    Copyright (c) 2007-2011 Cyrus Daboo. All rights reserved.
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

from pycalendar.parser import ParserContext
from pycalendar.stringutils import strtoul
from pycalendar.valueutils import ValueMixin

class PyCalendarDuration(ValueMixin):

    def __init__(self, duration = None, weeks=0, days=0, hours=0, minutes=0, seconds=0):
        self.mForward = True

        self.mWeeks = 0
        self.mDays = 0

        self.mHours = 0
        self.mMinutes = 0
        self.mSeconds = 0
        
        if duration is None:
            duration = (((weeks * 7 + days) * 24 + hours) * 60 + minutes) * 60 + seconds
        self.setDuration(duration)

    def duplicate(self):
        other = PyCalendarDuration(None)
        other.mForward = self.mForward

        other.mWeeks = self.mWeeks
        other.mDays = self.mDays

        other.mHours = self.mHours
        other.mMinutes = self.mMinutes
        other.mSeconds = self.mSeconds

        return other

    def __hash__(self):
        return hash(self.getTotalSeconds())

    def __eq__( self, comp ):
        return self.getTotalSeconds() == comp.getTotalSeconds()

    def __gt__( self, comp ):
        return self.getTotalSeconds() > comp.getTotalSeconds()

    def __lt__( self, comp ):
        return self.getTotalSeconds() <  comp.getTotalSeconds()

    def getTotalSeconds(self):
        return [1, -1][not self.mForward] \
                * (self.mSeconds + (self.mMinutes + (self.mHours + (self.mDays + (self.mWeeks * 7)) * 24) * 60) * 60)

    def setDuration(self, seconds):
        self.mForward = seconds >= 0

        remainder = seconds
        if remainder < 0:
            remainder = -remainder

        # Is it an exact number of weeks - if so use the weeks value, otherwise
        # days, hours, minutes, seconds
        if remainder % (7 * 24 * 60 * 60) == 0:
            self.mWeeks = remainder / (7 * 24 * 60 * 60)
            self.mDays = 0

            self.mHours = 0
            self.mMinutes = 0
            self.mSeconds = 0
        else:
            self.mSeconds = remainder % 60
            remainder -= self.mSeconds
            remainder /= 60

            self.mMinutes = remainder % 60
            remainder -= self.mMinutes
            remainder /= 60

            self.mHours = remainder % 24
            remainder -= self.mHours

            self.mDays = remainder / 24

            self.mWeeks = 0

    def getForward(self):
        return self.mForward

    def getWeeks(self):
        return self.mWeeks

    def getDays(self):
        return self.mDays

    def getHours(self):
        return self.mHours

    def getMinutes(self):
        return self.mMinutes

    def getSeconds(self):
        return self.mSeconds

    @classmethod
    def parseText(cls, data):
        dur = cls()
        dur.parse(data)
        return dur

    def parse(self, data):
        # parse format ([+]/-) "P" (dur-date / dur-time / dur-week)

        try:
            offset = 0
            maxoffset = len(data)
    
            # Look for +/-
            self.mForward = True
            if data[offset] in ('-', '+'):
                self.mForward = data[offset] == '+'
                offset += 1
    
            # Must have a 'P'
            if data[offset] != "P":
                raise ValueError
            offset += 1
            
            # Look for time
            if data[offset] != "T":
                # Must have a number
                num, offset = strtoul(data, offset)
    
                # Now look at character
                if data[offset] == "W":
                    # Have a number of weeks
                    self.mWeeks = num
                    offset += 1
    
                    # There cannot be anything else after this so just exit
                    if offset != maxoffset:
                        if data[offset] == "T" and ParserContext.INVALID_DURATION_VALUE != ParserContext.PARSER_RAISE:
                            return
                        raise ValueError
                    return
                elif data[offset] == "D":
                    # Have a number of days
                    self.mDays = num
                    offset += 1
    
                    # Look for more data - exit if none
                    if offset == maxoffset:
                        return
    
                    # Look for time - exit if none
                    if data[offset] != "T":
                        raise ValueError
                else:
                    # Error in format
                    raise ValueError
    
            # Have time
            offset += 1

            # Strictly speaking T must always be followed by time values, but some clients
            # send T with no additional text
            if offset == maxoffset:
                if ParserContext.INVALID_DURATION_VALUE == ParserContext.PARSER_RAISE:
                    raise ValueError
                else:
                    return
            num, offset = strtoul(data, offset)
    
            # Look for hour
            if data[offset] == "H":
                # Get hours
                self.mHours = num
                offset += 1
    
                # Look for more data - exit if none
                if offset == maxoffset:
                    return
    
                # Parse the next number
                num, offset = strtoul(data, offset)
    
            # Look for minute
            if data[offset] == "M":
                # Get hours
                self.mMinutes = num
                offset += 1
    
                # Look for more data - exit if none
                if offset == maxoffset:
                    return
    
                # Parse the next number
                num, offset = strtoul(data, offset)
    
            # Look for seconds
            if data[offset] == "S":
                # Get hours
                self.mSeconds = num
                offset += 1

                # No more data - exit
                if offset == maxoffset:
                    return
    
            raise ValueError

        except IndexError:
            raise ValueError

    def generate(self, os):
        try:
            if not self.mForward and (self.mWeeks or self.mDays or self.mHours or self.mMinutes or self.mSeconds):
                os.write("-")
            os.write("P")

            if self.mWeeks != 0:
                os.write("%dW" % (self.mWeeks,))
            else:
                if self.mDays != 0:
                    os.write("%dD" % (self.mDays,))

                if (self.mHours != 0) or (self.mMinutes != 0) or (self.mSeconds != 0):
                    os.write("T")

                    if self.mHours != 0:
                        os.write("%dH" % (self.mHours,))
    
                    if (self.mMinutes != 0) or ((self.mHours != 0) and (self.mSeconds != 0)):
                        os.write("%dM" % (self.mMinutes,))
    
                    if self.mSeconds != 0:
                        os.write("%dS" % (self.mSeconds,))
                elif self.mDays == 0:
                    os.write("T0S")
        except:
            pass
