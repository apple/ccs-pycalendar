##
#    Copyright (c) 2007 Cyrus Daboo. All rights reserved.
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

import re

class PyCalendarDuration(object):

    def __init__(self, duration=None, copyit=None):
        self.mForward = True

        self.mWeeks = 0
        self.mDays = 0

        self.mHours = 0
        self.mMinutes = 0
        self.mSeconds = 0
        
        if (duration is not None):
            self.setDuration(duration)
        elif (copyit is not None):
            self.mForward = copyit.mForward
    
            self.mWeeks = copyit.mWeeks
            self.mDays = copyit.mDays
    
            self.mHours = copyit.mHours
            self.mMinutes = copyit.mMinutes
            self.mSeconds = copyit.mSeconds

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

    def parse(self, data):
        # parse format ([+]/-) "P" (dur-date / dur-time / dur-week)

        regex = re.compile(r'([+/-]?)(P)([0-9]*)([DW]?)([T]?)([0-9]*)([HMS]?)([0-9]*)([MS]?)([0-9]*)([S]?)')
        st = regex.search(data).groups()
        st = [x for x in st if x != '']
        st.reverse()
        if len(st) == 0:
            return
        token = st.pop()

        # Look for +/-
        self.mForward = True
        if token == "-":
            self.mForward = False
            if len(st) == 0:
                return
            token = st.pop()
        elif token == "+":
            if len(st) == 0:
                return
            token = st.pop()

        # Must have a 'P'
        if token != "P":
            return
        
        # Look for time
        if len(st) == 0:
            return
        token = st.pop()
        if token != "T":
            # Must have a number
            num = int(token)

            # Now look at character
            if len(st) == 0:
                return
            token = st.pop()
            if token == "W":
                # Have a number of weeks
                self.mWeeks = num

                # There cannot bew anything else after this so just exit
                return
            elif token == "D":
                # Have a number of days
                self.mDays = num

                # Look for more data - exit if none
                if len(st) == 0:
                    return
                token = st.pop()

                # Look for time - exit if none
                if token != "T":
                    return
            else:
                # Error in format
                return

        # Have time
        if len(st) == 0:
            return
        token = st.pop()
        num = int(token)

        # Look for hour
        if len(st) == 0:
            return
        token = st.pop()
        if token == "H":
            # Get hours
            self.mHours = num

            # Look for more data - exit if none
            if len(st) == 0:
                return

            # Parse the next number
            token = st.pop()
            num = int(token)

            # Parse the next char
            if len(st) == 0:
                return
            token = st.pop()

        # Look for minute
        if token == "M":
            # Get hours
            self.mMinutes = num

            # Look for more data - exit if none
            if len(st) == 0:
                return

            # Parse the next number
            token = st.pop()
            num = int(token)

            # Parse the next char
            if len(st) == 0:
                return
            token = st.pop()

        # Look for seconds
        if token == "S":
            # Get hours
            self.mSeconds = num

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
