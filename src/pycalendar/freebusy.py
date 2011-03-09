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

class PyCalendarFreeBusy(object):

    FREE = 0
    BUSYTENTATIVE = 1
    BUSYUNAVAILABLE = 2
    BUSY = 3

    def __init__( self, type = None, period = None ):
        
        self.mType = type if type else PyCalendarFreeBusy.FREE
        self.mPeriod = period.duplicate() if period is not None else None

    def duplicate(self):
        return PyCalendarFreeBusy(self.mType, self.mPeriod)

    def setType( self, type ):
        self.mType = type

    def getType( self ):
        return self.mType

    def setPeriod( self, period ):
        self.mPeriod = period.duplicate()

    def getPeriod( self ):
        return self.mPeriod

    def isPeriodOverlap( self, period ):
        return self.mPeriod.isPeriodOverlap( period )

    def resolveOverlaps( self, fb ):
        # TODO:
        pass
