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

# vCard N value

from pycalendar.value import Value
from pycalendar.valueutils import WrapperValue
from pycalendar.vcard.n import N

class NValue(WrapperValue, Value):

    _wrappedClass = N
    _wrappedType = Value.VALUETYPE_N

Value.registerType(Value.VALUETYPE_N, NValue, None)
