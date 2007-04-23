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

#     2445 Component Header/Footer

cICalComponent_BEGINVCALENDAR = "BEGIN:VCALENDAR"
cICalComponent_ENDVCALENDAR = "END:VCALENDAR"
cICalComponent_BEGINVEVENT = "BEGIN:VEVENT"
cICalComponent_ENDVEVENT = "END:VEVENT"
cICalComponent_BEGINVTODO = "BEGIN:VTODO"
cICalComponent_ENDVTODO = "END:VTODO"
cICalComponent_BEGINVJOURNAL = "BEGIN:VJOURNAL"
cICalComponent_ENDVJOURNAL = "END:VJOURNAL"
cICalComponent_BEGINVFREEBUSY = "BEGIN:VFREEBUSY"
cICalComponent_ENDVFREEBUSY = "END:VFREEBUSY"
cICalComponent_BEGINVTIMEZONE = "BEGIN:VTIMEZONE"
cICalComponent_ENDVTIMEZONE = "END:VTIMEZONE"
cICalComponent_BEGINVALARM = "BEGIN:VALARM"
cICalComponent_ENDVALARM = "END:VALARM"

#     Pseudo components
cICalComponent_BEGINSTANDARD = "BEGIN:STANDARD"
cICalComponent_ENDSTANDARD = "END:STANDARD"
cICalComponent_BEGINDAYLIGHT = "BEGIN:DAYLIGHT"
cICalComponent_ENDDAYLIGHT = "END:DAYLIGHT"

#     2445 Calendar Property Atrributes

#     2445 Section 4.2
cICalAttribute_ALTREP = "ALTREP"
cICalAttribute_CN = "CN"
cICalAttribute_CUTYPE = "CUTYPE"
cICalAttribute_DELEGATED_FROM = "DELEGATED-FROM"
cICalAttribute_DELEGATED_TO = "DELEGATED-TO"
cICalAttribute_DIR = "DIR"
cICalAttribute_ENCODING = "ENCODING"
cICalAttribute_FMTTYPE = "FMTTYPE"
cICalAttribute_FBTYPE = "FBTYPE"
cICalAttribute_LANGUAGE = "LANGUAGE"
cICalAttribute_MEMBER = "MEMBER"
cICalAttribute_PARTSTAT = "PARTSTAT"
cICalAttribute_RANGE = "RANGE"
cICalAttribute_RELATED = "RELATED"
cICalAttribute_RELTYPE = "RELTYPE"
cICalAttribute_ROLE = "ROLE"
cICalAttribute_RSVP = "RSVP"
cICalAttribute_RSVP_TRUE = "TRUE"
cICalAttribute_RSVP_FALSE = "FALSE"
cICalAttribute_SENT_BY = "SENT-BY"
cICalAttribute_TZID = "TZID"
cICalAttribute_VALUE = "VALUE"

#     2445 Section 4.2.9
cICalAttribute_FBTYPE_FREE = "FREE"
cICalAttribute_FBTYPE_BUSY = "BUSY"
cICalAttribute_FBTYPE_BUSYUNAVAILABLE = "BUSY-UNAVAILABLE"
cICalAttribute_FBTYPE_BUSYTENTATIVE = "BUSY-TENTATIVE"

#     2445 Section 4.2.12
ePartStat_NeedsAction = 0
ePartStat_Accepted = 1
ePartStat_Declined = 2
ePartStat_Tentative = 3
ePartStat_Delegated = 4
ePartStat_Completed = 5
ePartStat_InProcess = 6

cICalAttribute_PARTSTAT_NEEDSACTION = "NEEDS-ACTION"
cICalAttribute_PARTSTAT_ACCEPTED = "ACCEPTED"
cICalAttribute_PARTSTAT_DECLINED = "DECLINED"
cICalAttribute_PARTSTAT_TENTATIVE = "TENTATIVE"
cICalAttribute_PARTSTAT_DELEGATED = "DELEGATED"
cICalAttribute_PARTSTAT_COMPLETED = "COMPLETE"
cICalAttribute_PARTSTAT_INPROCESS = "IN-PROCESS"

#     2445 Section 4.2.13
cICalAttribute_RANGE_THISANDFUTURE = "THISANDFUTURE"
cICalAttribute_RANGE_THISANDPRIOR = "THISANDPRIOR"

#     2445 Section 4.2.14
cICalAttribute_RELATED_START = "START"
cICalAttribute_RELATED_END = "END"

#     2445 Section 4.2.16
ePartRole_Chair = 0
ePartRole_Required = 1
ePartRole_Optional = 2
ePartRole_Non = 3

cICalAttribute_ROLE_CHAIR = "CHAIR"
cICalAttribute_ROLE_REQ_PART = "REQ-PARTICIPANT"
cICalAttribute_ROLE_OPT_PART = "OPT-PARTICIPANT"
cICalAttribute_ROLE_NON_PART = "NON-PARTICIPANT"

#     2445 Value types

#     2445 Section 4.3
cICalValue_BINARY = "BINARY"
cICalValue_BOOLEAN = "BOOLEAN"
cICalValue_CAL_ADDRESS = "CAL-ADDRESS"
cICalValue_DATE = "DATE"
cICalValue_DATE_TIME = "DATE-TIME"
cICalValue_DURATION = "DURATION"
cICalValue_FLOAT = "FLOAT"
cICalValue_INTEGER = "INTEGER"
cICalValue_PERIOD = "PERIOD"
cICalValue_RECUR = "RECUR"
cICalValue_TEXT = "TEXT"
cICalValue_TIME = "TIME"
cICalValue_URI = "URI"
cICalValue_UTC_OFFSET = "UTC-OFFSET"

#     2445 Calendar Properties

#     2445 Section  4.7

cICalProperty_CALSCALE = "CALSCALE"
cICalProperty_METHOD = "METHOD"
cICalProperty_PRODID = "PRODID"
cICalProperty_VERSION = "VERSION"

#     Apple Extensions
cICalProperty_XWRCALNAME = "X-WR-CALNAME"
cICalProperty_XWRCALDESC = "X-WR-CALDESC"

#     2445 Componenty Property names

#     2445 Section 4.8.1
cICalProperty_ATTACH = "ATTACH"
cICalProperty_CATEGORIES = "CATEGORIES"
cICalProperty_CLASS = "CLASS"
cICalProperty_COMMENT = "COMMENT"
cICalProperty_DESCRIPTION = "DESCRIPTION"
cICalProperty_GEO = "GEO"
cICalProperty_LOCATION = "LOCATION"
cICalProperty_PERCENT_COMPLETE = "PERCENT-COMPLETE"
cICalProperty_PRIORITY = "PRIORITY"
cICalProperty_RESOURCES = "RESOURCES"
cICalProperty_STATUS = "STATUS"
cICalProperty_SUMMARY = "SUMMARY"

#     2445 Section 4.8.2
cICalProperty_COMPLETED = "COMPLETED"
cICalProperty_DTEND = "DTEND"
cICalProperty_DUE = "DUE"
cICalProperty_DTSTART = "DTSTART"
cICalProperty_DURATION = "DURATION"
cICalProperty_FREEBUSY = "FREEBUSY"
cICalProperty_TRANSP = "TRANSP"
cICalProperty_OPAQUE = "OPAQUE"
cICalProperty_TRANSPARENT = "TRANSPARENT"

#     2445 Section 4.8.3
cICalProperty_TZID = "TZID"
cICalProperty_TZNAME = "TZNAME"
cICalProperty_TZOFFSETFROM = "TZOFFSETFROM"
cICalProperty_TZOFFSETTO = "TZOFFSETTO"
cICalProperty_TZURL = "TZURL"

#     2445 Section 4.8.4
cICalProperty_ATTENDEE = "ATTENDEE"
cICalProperty_CONTACT = "CONTACT"
cICalProperty_ORGANIZER = "ORGANIZER"
cICalProperty_RECURRENCE_ID = "RECURRENCE-ID"
cICalProperty_RELATED_TO = "RELATED-TO"
cICalProperty_URL = "URL"
cICalProperty_UID = "UID"

#     2445 Section 4.8.5
cICalProperty_EXDATE = "EXDATE"
cICalProperty_EXRULE = "EXRULE"
cICalProperty_RDATE = "RDATE"
cICalProperty_RRULE = "RRULE"

#     2445 Section 4.8.6
cICalProperty_ACTION = "ACTION"
cICalProperty_REPEAT = "REPEAT"
cICalProperty_TRIGGER = "TRIGGER"

#     2445 Section 4.8.7
cICalProperty_CREATED = "CREATED"
cICalProperty_DTSTAMP = "DTSTAMP"
cICalProperty_LAST_MODIFIED = "LAST-MODIFIED"
cICalProperty_SEQUENCE = "SEQUENCE"

#     2445 Section 4.8.8.2
cICalProperty_REQUEST_STATUS = "REQUEST-STATUS"

#     Enums
#     Use ascending order for sensible sorting

#     2445 Section 4.3.10

eRecurrence_SECONDLY = 0
eRecurrence_MINUTELY = 1
eRecurrence_HOURLY = 2
eRecurrence_DAILY = 3
eRecurrence_WEEKLY = 4
eRecurrence_MONTHLY = 5
eRecurrence_YEARLY = 6

cICalValue_RECUR_FREQ = "FREQ="
cICalValue_RECUR_FREQ_LEN = 5

cICalValue_RECUR_SECONDLY = "SECONDLY"
cICalValue_RECUR_MINUTELY = "MINUTELY"
cICalValue_RECUR_HOURLY = "HOURLY"
cICalValue_RECUR_DAILY = "DAILY"
cICalValue_RECUR_WEEKLY = "WEEKLY"
cICalValue_RECUR_MONTHLY = "MONTHLY"
cICalValue_RECUR_YEARLY = "YEARLY"

cICalValue_RECUR_UNTIL = "UNTIL="
cICalValue_RECUR_COUNT = "COUNT="

cICalValue_RECUR_INTERVAL = "INTERVAL="
cICalValue_RECUR_BYSECOND = "BYSECOND="
cICalValue_RECUR_BYMINUTE = "BYMINUTE="
cICalValue_RECUR_BYHOUR = "BYHOUR="
cICalValue_RECUR_BYDAY = "BYDAY="
cICalValue_RECUR_BYMONTHDAY = "BYMONTHDAY="
cICalValue_RECUR_BYYEARDAY = "BYYEARDAY="
cICalValue_RECUR_BYWEEKNO = "BYWEEKNO="
cICalValue_RECUR_BYMONTH = "BYMONTH="
cICalValue_RECUR_BYSETPOS = "BYSETPOS="
cICalValue_RECUR_WKST = "WKST="

eRecurrence_WEEKDAY_SU = 0
eRecurrence_WEEKDAY_MO = 1
eRecurrence_WEEKDAY_TU = 2
eRecurrence_WEEKDAY_WE = 3
eRecurrence_WEEKDAY_TH = 4
eRecurrence_WEEKDAY_FR = 5
eRecurrence_WEEKDAY_SA = 6

cICalValue_RECUR_WEEKDAY_SU = "SU"
cICalValue_RECUR_WEEKDAY_MO = "MO"
cICalValue_RECUR_WEEKDAY_TU = "TU"
cICalValue_RECUR_WEEKDAY_WE = "WE"
cICalValue_RECUR_WEEKDAY_TH = "TH"
cICalValue_RECUR_WEEKDAY_FR = "FR"
cICalValue_RECUR_WEEKDAY_SA = "SA"

#     2445 Section 4.8.1.11
eStatus_VEvent_None = 0
eStatus_VEvent_Confirmed = 1
eStatus_VEvent_Tentative = 2
eStatus_VEvent_Cancelled = 3

eStatus_VToDo_None = 0
eStatus_VToDo_NeedsAction = 1
eStatus_VToDo_InProcess = 2
eStatus_VToDo_Completed = 3
eStatus_VToDo_Cancelled = 4

eStatus_VJournal_None = 0
eStatus_VJournal_Final = 1
eStatus_VJournal_Draft = 2
eStatus_VJournal_Cancelled = 3

cICalProperty_STATUS_TENTATIVE = "TENTATIVE"
cICalProperty_STATUS_CONFIRMED = "CONFIRMED"
cICalProperty_STATUS_CANCELLED = "CANCELLED"
cICalProperty_STATUS_NEEDS_ACTION = "NEEDS-ACTION"
cICalProperty_STATUS_COMPLETED = "COMPLETED"
cICalProperty_STATUS_IN_PROCESS = "IN-PROCESS"
cICalProperty_STATUS_DRAFT = "DRAFT"
cICalProperty_STATUS_FINAL = "FINAL"

#     2445 Section 4.8.6.1
eAction_VAlarm_Audio = 0
eAction_VAlarm_Display = 1
eAction_VAlarm_Email = 2
eAction_VAlarm_Procedure = 3
eAction_VAlarm_Unknown = 4

cICalProperty_ACTION_AUDIO = "AUDIO"
cICalProperty_ACTION_DISPLAY = "DISPLAY"
cICalProperty_ACTION_EMAIL = "EMAIL"
cICalProperty_ACTION_PROCEDURE = "PROCEDURE"


#     Mulberry extensions
cICalProperty_X_PRIVATE_RURL = "X-MULBERRY-PRIVATE-RURL"
cICalProperty_X_PRIVATE_ETAG = "X-MULBERRY-PRIVATE-ETAG"

cICalProperty_ACTION_X_SPEAKTEXT = "X-MULBERRY-SPEAK-TEXT"
cICalProperty_ALARM_X_LASTTRIGGER = "X-MULBERRY-LAST-TRIGGER"

cICalProperty_ALARM_X_ALARMSTATUS = "X-MULBERRY-ALARM-STATUS"

eAlarm_Status_Pending = 0
eAlarm_Status_Completed = 1
eAlarm_Status_Disabled = 2

cICalProperty_ALARM_X_ALARMSTATUS_PENDING = "PENDING"
cICalProperty_ALARM_X_ALARMSTATUS_COMPLETED = "COMPLETED"
cICalProperty_ALARM_X_ALARMSTATUS_DISABLED = "DISABLED"

cICalAttribute_ORGANIZER_X_IDENTITY = "X-MULBERRY-IDENTITY"
cICalAttribute_ATTENDEE_X_NEEDS_ITIP = "X-MULBERRY-NEEDS-ITIP"
