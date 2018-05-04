from __future__ import absolute_import
##
#    Copyright (c) 2007-2015 Cyrus Daboo. All rights reserved.
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

# Import these to register the values

from . import binaryvalue
from . import caladdressvalue
from . import datetimevalue
from . import durationvalue
from . import floatvalue
from . import geovalue
from .icalendar import recurrencevalue
from .icalendar import requeststatusvalue
from . import integervalue
from . import multivalue
from . import periodvalue
from . import textvalue
from . import unknownvalue
from . import urivalue
from . import utcoffsetvalue
from .vcard import adrvalue
from .vcard import nvalue
from .vcard import orgvalue

# Import these to register the components

from .icalendar import available
from .icalendar import valarm
from .icalendar import vavailability
from .icalendar import vevent
from .icalendar import vfreebusy
from .icalendar import vjournal
from .icalendar import vpoll
from .icalendar import vote
from .icalendar import vtimezone
from .icalendar import vtimezonedaylight
from .icalendar import vtimezonestandard
from .icalendar import vtodo
from .icalendar import vunknown
from .icalendar import vvoter
