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
            self.mDuration = self.mEnd.subtract( self.mStart )
            self.mUseDuration = False
        elif (start is not None) and (duration is not None):
            self.mStart = start
            self.mDuration = duration
            self.mEnd = self.mStart.add( self.mDuration )
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

    def equals( self, comp ):
        return self.mStart.equals( comp.mStart ) and self.mEnd.equals( comp.mEnd )

    def gt( self, comp ):
        return self.mStart.gt( comp )

    def lt( self, comp ):
        return self.mStart.lt( comp.mStart ) \
                or ( self.mStart.eq( comp.mStart ) and self.mEnd.lt( comp.mEnd ) )

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
                self.mDuration = self.mEnd.subtract( self.mStart )

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
        return dt.ge( self.mStart ) and dt.lt( self.mEnd )

    def isDateBeforePeriod( self, dt ):
        # Inclusive start
        return dt.lt( self.mStart )

    def isDateAfterPeriod( self, dt ):
        # Exclusive end
        return dt.ge( self.mEnd )

    def isPeriodOverlap( self, p ):
        # Inclusive start, exclusive end
        return not ( self.mStart.ge( p.mEnd ) or self.mEnd.le( p.mStart ) )

    def describeDuration( self ):
        return ""
