##
#    Copyright (c) 2011 Cyrus Daboo. All rights reserved.
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

from pycalendar import definitions
from pycalendar.validation import partial, PropertyValueChecks

ICALENDAR_VALUE_CHECKS = {
    definitions.cICalProperty_CALSCALE: partial(PropertyValueChecks.stringValue, "GREGORIAN"),
    definitions.cICalProperty_VERSION: partial(PropertyValueChecks.stringValue, "2.0"),

    definitions.cICalProperty_PERCENT_COMPLETE: partial(PropertyValueChecks.numericRange, 0, 100),
    definitions.cICalProperty_PRIORITY: partial(PropertyValueChecks.numericRange, 0, 9),

    definitions.cICalProperty_COMPLETED: PropertyValueChecks.alwaysUTC,

    definitions.cICalProperty_REPEAT: PropertyValueChecks.positiveIntegerOrZero,

    definitions.cICalProperty_CREATED: PropertyValueChecks.alwaysUTC,
    definitions.cICalProperty_DTSTAMP: PropertyValueChecks.alwaysUTC,
    definitions.cICalProperty_LAST_MODIFIED: PropertyValueChecks.alwaysUTC,
    definitions.cICalProperty_SEQUENCE: PropertyValueChecks.positiveIntegerOrZero,
}
