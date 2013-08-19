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

# Import these to register the values

import binaryvalue
import caladdressvalue
import datetimevalue
import durationvalue
import floatvalue
import geovalue
import icalendar.recurrencevalue
import icalendar.requeststatusvalue
import integervalue
import multivalue
import periodvalue
import textvalue
import unknownvalue
import urivalue
import utcoffsetvalue
import vcard.adrvalue
import vcard.nvalue
import vcard.orgvalue

# Import these to register the components

import icalendar.available
import icalendar.valarm
import icalendar.vavailability
import icalendar.vevent
import icalendar.vfreebusy
import icalendar.vjournal
import icalendar.vtimezone
import icalendar.vtimezonedaylight
import icalendar.vtimezonestandard
import icalendar.vtodo
import icalendar.vunknown

# Import these to force static initialisation
#import property
