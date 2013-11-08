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

class DateTime(object):
    """
    A date-time object that wraps the tzdb wall-clock/utc style date-time information
    and that can generate appropriate localtime or UTC offsets based on Zone/Rule offsets.
    """

    def __init__(self, dt, mode):
        self.dt = dt
        self.mode = mode


    def __repr__(self):
        return str(self.dt)


    def compareDateTime(self, other):
        return self.dt.compareDateTime(other.dt)


    def getLocaltime(self, offset, stdoffset):
        new_dt = self.dt.duplicate()
        if self.mode == "u":
            new_dt.offsetSeconds(offset)
        elif self.mode == "s":
            new_dt.offsetSeconds(-stdoffset + offset)
        return new_dt


    def getUTC(self, offset, stdoffset):
        new_dt = self.dt.duplicate()
        if self.mode == "u":
            pass
        elif self.mode == "s":
            new_dt.offsetSeconds(-stdoffset)
        else:
            new_dt.offsetSeconds(-offset)
        return new_dt
