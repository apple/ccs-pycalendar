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


LONG = 0;
SHORT = 1;
ABBREVIATED = 2;

cLongDays = [ "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" ];

cShortDays = [ "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat" ];

cAbbrevDays = [ "S", "M", "T", "W", "T", "F", "S" ];

cLongMonths = [ "", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December" ];

cShortMonths = [ "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]

cAbbrevMonths = [ "", "J", "F", "M", "A", "M", "J",
                  "J", "A", "S", "O", "N", "D" ]

s24HourTime = False;
sDDMMDate = False;

#     0..6 - Sunday - Saturday
def getDay(day, strl):
    return {LONG: cLongDays[day], SHORT: cShortDays[day], ABBREVIATED: cAbbrevDays[day]}[strl]

#     1..12 - January - December
def getMonth(month, strl):
    return {LONG: cLongMonths[month], SHORT: cShortMonths[month], ABBREVIATED: cAbbrevMonths[month]}[strl]

#     Use 24 hour time display
def use24HourTime():

    # TODO: get 24 hour option from system prefs

    return s24HourTime;

#     Use DD/MM date display
def useDDMMDate():

    # TODO: get 24 hour option from system prefs

    return sDDMMDate;

