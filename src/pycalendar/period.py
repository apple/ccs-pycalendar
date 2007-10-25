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

import cStringIO as StringIO

from datetime import PyCalendarDateTime
from duration import PyCalendarDuration

class PyCalendarPeriod(object):

    def __init__( self, start = None, end = None, duration = None, copyit = None ):
        
        if (start is not None) and (end is not None):
            self.mStart = start
            self.mEnd = end
            self.mDuration = self.mEnd - self.mStart
            self.mUseDuration = False
        elif (start is not None) and (duration is not None):
            self.mStart = start
            self.mDuration = duration
            self.mEnd = self.mStart + self.mDuration
            self.mUseDuration = True
        elif (copyit is not None):
            self.mStart = PyCalendarDateTime(copyit=copyit.mStart)
            self.mEnd = PyCalendarDateTime(copyit=copyit.mEnd)
            self.mDuration = PyCalendarDuration(copyit=copyit.mDuration)
            self.mUseDuration = copyit.mUseDuration
        else:
            self.mStart = PyCalendarDateTime()
            self.mEnd = PyCalendarDateTime()
            self.mDuration = PyCalendarDuration()
            self.mUseDuration = False

    def __repr__(self):
        os = StringIO.StringIO()
        self.generate(os)
        return os.getvalue()

    def __eq__( self, comp ):
        return self.mStart == comp.mStart and self.mEnd == comp.mEnd

    def __gt__( self, comp ):
        return self.mStart > comp

    def __lt__( self, comp ):
        return self.mStart <  comp.mStart  \
                or ( self.mStart == comp.mStart ) and self.mEnd < comp.mEnd

    def parse( self, data ):
        slash_pos = data.find( '/' )
        if slash_pos != -1:
            start = data[0:slash_pos]
            end = data[slash_pos + 1:]

            self.mStart.parse( start )
            if end[0] == 'P':
                self.mDuration.parse( end )
                self.mUseDuration = True
                self.mEnd = self.mStart.add( self.mDuration )
            else:
                self.mEnd.parse( end )
                self.mUseDuration = False
                self.mDuration = self.mEnd - self.mStart

    def generate( self, os ):
        try:
            self.mStart.generate( os )
            os.write( "/" )
            if self.mUseDuration:
                self.mDuration.generate( os )
            else:
                self.mEnd.generate( os )
        except:
            pass

    def getStart( self ):
        return self.mStart

    def getEnd( self ):
        return self.mEnd

    def getDuration( self ):
        return self.mDuration

    def isDateWithinPeriod( self, dt ):
        # Inclusive start, exclusive end
        return dt >= self.mStart and dt < self.mEnd

    def isDateBeforePeriod( self, dt ):
        # Inclusive start
        return dt < self.mStart

    def isDateAfterPeriod( self, dt ):
        # Exclusive end
        return dt >= self.mEnd

    def isPeriodOverlap( self, p ):
        # Inclusive start, exclusive end
        return not ( self.mStart >= p.mEnd or self.mEnd <= p.mStart )

    def describeDuration( self ):
        return ""
