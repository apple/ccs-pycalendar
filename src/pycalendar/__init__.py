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

__all__ = [
    "attribute",
    "caladdressvalue",
    "calendar",
    "datetime",
    "datetimevalue",
    "definitions",
    "dummyvalue",
    "duration",
    "durationvalue",
    "freebusy",
    "integervalue",
    "locale",
    "multivalue",
    "period",
    "periodvalue",
    "plaintextvalue",
    "property",
    "recurrence",
    "recurrencevalue",
    "textvalue",
    "timezone",
    "urivalue",
    "utcoffsetvalue",
    "utils",
    "value",
    "vevent",
    "vfreebusy",
    "stringutils"
]

# Import these to register the values
import caladdressvalue, datetimevalue, dummyvalue, durationvalue, \
        integervalue, multivalue, periodvalue, recurrencevalue, \
        textvalue, urivalue, utcoffsetvalue
    
# Import these to force static initialisation
import property
