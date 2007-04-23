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

from period import PyCalendarPeriod

class PyCalendarFreeBusy(object):

    FREE = 0
    BUSYTENTATIVE = 1
    BUSYUNAVAILABLE = 2
    BUSY = 3

    def __init__( self, type = None, period = None, copyit = None ):
        
        if type and period:
            self.mType = type
            self.mPeriod = PyCalendarPeriod( copyit=period )
        elif type:
            self.mType = type
        elif copyit:
            self.mType = copyit.mType
            self.mPeriod = PyCalendarPeriod( copyit=copyit.mPeriod )
        else:
            self.mType = PyCalendarFreeBusy.FREE

    def setType( self, type ):
        self.mType = type

    def getType( self ):
        return self.mType

    def setPeriod( self, period ):
        self.mPeriod = PyCalendarPeriod( copyit=period )

    def getPeriod( self ):
        return self.mPeriod

    def isPeriodOverlap( self, period ):
        return self.mPeriod.isPeriodOverlap( period )

    def resolveOverlaps( self, fb ):
        # TODO:
        pass
