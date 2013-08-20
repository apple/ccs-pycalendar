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

#     5545 Components

cICalComponent_VCALENDAR = "VCALENDAR"
cICalComponent_VEVENT = "VEVENT"
cICalComponent_VTODO = "VTODO"
cICalComponent_VJOURNAL = "VJOURNAL"
cICalComponent_VFREEBUSY = "VFREEBUSY"
cICalComponent_VTIMEZONE = "VTIMEZONE"
cICalComponent_VALARM = "VALARM"
cICalComponent_STANDARD = "STANDARD"
cICalComponent_DAYLIGHT = "DAYLIGHT"
cICalComponent_UNKNOWN = "UNKNOWN"

#     5545 Calendar Property Parameters

#     5545 Section 3.2
cICalParameter_ALTREP = "ALTREP"
cICalParameter_CN = "CN"
cICalParameter_CUTYPE = "CUTYPE"
cICalParameter_DELEGATED_FROM = "DELEGATED-FROM"
cICalParameter_DELEGATED_TO = "DELEGATED-TO"
cICalParameter_DIR = "DIR"
cICalParameter_ENCODING = "ENCODING"
cICalParameter_FMTTYPE = "FMTTYPE"
cICalParameter_FBTYPE = "FBTYPE"
cICalParameter_LANGUAGE = "LANGUAGE"
cICalParameter_MEMBER = "MEMBER"
cICalParameter_PARTSTAT = "PARTSTAT"
cICalParameter_RANGE = "RANGE"
cICalParameter_RELATED = "RELATED"
cICalParameter_RELTYPE = "RELTYPE"
cICalParameter_ROLE = "ROLE"
cICalParameter_RSVP = "RSVP"
cICalParameter_RSVP_TRUE = "TRUE"
cICalParameter_RSVP_FALSE = "FALSE"
cICalParameter_SENT_BY = "SENT-BY"
cICalParameter_TZID = "TZID"
cICalParameter_VALUE = "VALUE"

#     5545 Section 3.2.9
cICalParameter_FBTYPE_FREE = "FREE"
cICalParameter_FBTYPE_BUSY = "BUSY"
cICalParameter_FBTYPE_BUSYUNAVAILABLE = "BUSY-UNAVAILABLE"
cICalParameter_FBTYPE_BUSYTENTATIVE = "BUSY-TENTATIVE"

#     5545 Section 3.2.12
ePartStat_NeedsAction = 0
ePartStat_Accepted = 1
ePartStat_Declined = 2
ePartStat_Tentative = 3
ePartStat_Delegated = 4
ePartStat_Completed = 5
ePartStat_InProcess = 6

cICalParameter_PARTSTAT_NEEDSACTION = "NEEDS-ACTION"
cICalParameter_PARTSTAT_ACCEPTED = "ACCEPTED"
cICalParameter_PARTSTAT_DECLINED = "DECLINED"
cICalParameter_PARTSTAT_TENTATIVE = "TENTATIVE"
cICalParameter_PARTSTAT_DELEGATED = "DELEGATED"
cICalParameter_PARTSTAT_COMPLETED = "COMPLETE"
cICalParameter_PARTSTAT_INPROCESS = "IN-PROCESS"

#     5545 Section 3.2.13
cICalParameter_RANGE_THISANDFUTURE = "THISANDFUTURE"
cICalParameter_RANGE_THISANDPRIOR = "THISANDPRIOR"      # 2445 only

#     5545 Section 3.2.14
cICalParameter_RELATED_START = "START"
cICalParameter_RELATED_END = "END"

#     5545 Section 3.2.16
ePartRole_Chair = 0
ePartRole_Required = 1
ePartRole_Optional = 2
ePartRole_Non = 3

cICalParameter_ROLE_CHAIR = "CHAIR"
cICalParameter_ROLE_REQ_PART = "REQ-PARTICIPANT"
cICalParameter_ROLE_OPT_PART = "OPT-PARTICIPANT"
cICalParameter_ROLE_NON_PART = "NON-PARTICIPANT"

#     5545 Section 3.2.3
eCutype_Individual = 0
eCutype_Group = 1
eCutype_Resource = 2
eCutype_Room = 3
eCutype_Unknown = 4

cICalParameter_CUTYPE_INDIVIDUAL = "INDIVIDUAL"
cICalParameter_CUTYPE_GROUP = "GROUP"
cICalParameter_CUTYPE_RESOURCE = "RESOURCE"
cICalParameter_CUTYPE_ROOM = "ROOM"
cICalParameter_CUTYPE_UNKNOWN = "UNKNOWN"

#     5545 Value types

#     5545 Section 3.3
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

#     5545 Calendar Properties

#     5545 Section  3.7

cICalProperty_CALSCALE = "CALSCALE"
cICalProperty_METHOD = "METHOD"
cICalProperty_PRODID = "PRODID"
cICalProperty_VERSION = "VERSION"

#     Apple Extensions
cICalProperty_XWRCALNAME = "X-WR-CALNAME"
cICalProperty_XWRCALDESC = "X-WR-CALDESC"
cICalProperty_XWRALARMUID = "X-WR-ALARMUID"

#     5545 Component Property names

#     5545 Section 3.8.1
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

#     5545 Section 3.8.2
cICalProperty_COMPLETED = "COMPLETED"
cICalProperty_DTEND = "DTEND"
cICalProperty_DUE = "DUE"
cICalProperty_DTSTART = "DTSTART"
cICalProperty_DURATION = "DURATION"
cICalProperty_FREEBUSY = "FREEBUSY"
cICalProperty_TRANSP = "TRANSP"
cICalProperty_OPAQUE = "OPAQUE"
cICalProperty_TRANSPARENT = "TRANSPARENT"

#     5545 Section 3.8.3
cICalProperty_TZID = "TZID"
cICalProperty_TZNAME = "TZNAME"
cICalProperty_TZOFFSETFROM = "TZOFFSETFROM"
cICalProperty_TZOFFSETTO = "TZOFFSETTO"
cICalProperty_TZURL = "TZURL"

#     5545 Section 3.8.4
cICalProperty_ATTENDEE = "ATTENDEE"
cICalProperty_CONTACT = "CONTACT"
cICalProperty_ORGANIZER = "ORGANIZER"
cICalProperty_RECURRENCE_ID = "RECURRENCE-ID"
cICalProperty_RELATED_TO = "RELATED-TO"
cICalProperty_URL = "URL"
cICalProperty_UID = "UID"

#     5545 Section 3.8.5
cICalProperty_EXDATE = "EXDATE"
cICalProperty_EXRULE = "EXRULE"     # 2445 only
cICalProperty_RDATE = "RDATE"
cICalProperty_RRULE = "RRULE"

#     5545 Section 3.8.6
cICalProperty_ACTION = "ACTION"
cICalProperty_REPEAT = "REPEAT"
cICalProperty_TRIGGER = "TRIGGER"

#     5545 Section 3.8.7
cICalProperty_CREATED = "CREATED"
cICalProperty_DTSTAMP = "DTSTAMP"
cICalProperty_LAST_MODIFIED = "LAST-MODIFIED"
cICalProperty_SEQUENCE = "SEQUENCE"

#     5545 Section 3.8.8.3
cICalProperty_REQUEST_STATUS = "REQUEST-STATUS"

#     Enums
#     Use ascending order for sensible sorting

#     5545 Section 3.3.10

eRecurrence_SECONDLY = 0
eRecurrence_MINUTELY = 1
eRecurrence_HOURLY = 2
eRecurrence_DAILY = 3
eRecurrence_WEEKLY = 4
eRecurrence_MONTHLY = 5
eRecurrence_YEARLY = 6

eRecurrence_FREQ = 0
eRecurrence_UNTIL = 1
eRecurrence_COUNT = 2
eRecurrence_INTERVAL = 3
eRecurrence_BYSECOND = 4
eRecurrence_BYMINUTE = 5
eRecurrence_BYHOUR = 6
eRecurrence_BYDAY = 7
eRecurrence_BYMONTHDAY = 8
eRecurrence_BYYEARDAY = 9
eRecurrence_BYWEEKNO = 10
eRecurrence_BYMONTH = 11
eRecurrence_BYSETPOS = 12
eRecurrence_WKST = 13

cICalValue_RECUR_FREQ = "FREQ"
cICalValue_RECUR_FREQ_LEN = 5

cICalValue_RECUR_SECONDLY = "SECONDLY"
cICalValue_RECUR_MINUTELY = "MINUTELY"
cICalValue_RECUR_HOURLY = "HOURLY"
cICalValue_RECUR_DAILY = "DAILY"
cICalValue_RECUR_WEEKLY = "WEEKLY"
cICalValue_RECUR_MONTHLY = "MONTHLY"
cICalValue_RECUR_YEARLY = "YEARLY"

cICalValue_RECUR_UNTIL = "UNTIL"
cICalValue_RECUR_COUNT = "COUNT"

cICalValue_RECUR_INTERVAL = "INTERVAL"
cICalValue_RECUR_BYSECOND = "BYSECOND"
cICalValue_RECUR_BYMINUTE = "BYMINUTE"
cICalValue_RECUR_BYHOUR = "BYHOUR"
cICalValue_RECUR_BYDAY = "BYDAY"
cICalValue_RECUR_BYMONTHDAY = "BYMONTHDAY"
cICalValue_RECUR_BYYEARDAY = "BYYEARDAY"
cICalValue_RECUR_BYWEEKNO = "BYWEEKNO"
cICalValue_RECUR_BYMONTH = "BYMONTH"
cICalValue_RECUR_BYSETPOS = "BYSETPOS"
cICalValue_RECUR_WKST = "WKST"

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

#     5545 Section 3.8.1.11
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

#     5545 Section 3.8.6.1
eAction_VAlarm_Audio = 0
eAction_VAlarm_Display = 1
eAction_VAlarm_Email = 2
eAction_VAlarm_Procedure = 3
eAction_VAlarm_Unknown = 4

cICalProperty_ACTION_AUDIO = "AUDIO"
cICalProperty_ACTION_DISPLAY = "DISPLAY"
cICalProperty_ACTION_EMAIL = "EMAIL"
cICalProperty_ACTION_PROCEDURE = "PROCEDURE"

#     Extensions: draft-daboo-calendar-availability-02

#     Section 3.1
cICalComponent_VAVAILABILITY = "VAVAILABILITY"
cICalComponent_AVAILABLE = "AVAILABLE"

#     Section 3.2
cICalProperty_BUSYTYPE = "BUSYTYPE"


#     Extensions: draft-daboo-valarm-extensions-03

#     Section 5
eAction_VAlarm_URI = 5
cICalProperty_ACTION_URI = "URI"

#     Section 7.1
cICalProperty_ACKNOWLEDGED = "ACKNOWLEDGED"

eAction_VAlarm_None = 6
cICalProperty_ACTION_NONE = "NONE"


#    Extensions: draft-york-vpoll-00.txt

#    Section 4.1
cICalParamater_PUBLIC_COMMENT = "PUBLIC-COMMENT"
cICalParamater_RESPONSE = "RESPONSE"
cICalParamater_STAY_INFORMED = "STAY-INFORMED"

#    Section 4.2
cICalProperty_ACCEPT_RESPONSE = "ACCEPT-RESPONSE"
cICalProperty_POLL_ITEM_ID = "POLL-ITEM-ID"
cICalProperty_POLL_MODE = "POLL-MODE"
cICalProperty_POLL_MODE_BASIC = "BASIC"
cICalProperty_POLL_PROPERTIES = "POLL-PROPERTIES"
cICalProperty_VOTER = "VOTER"

#    Section 4.3
cICalComponent_VPOLL = "VPOLL"


#     Mulberry extensions
cICalProperty_ACTION_X_SPEAKTEXT = "X-MULBERRY-SPEAK-TEXT"
cICalProperty_ALARM_X_LASTTRIGGER = "X-MULBERRY-LAST-TRIGGER"

cICalProperty_ALARM_X_ALARMSTATUS = "X-MULBERRY-ALARM-STATUS"

eAlarm_Status_Pending = 0
eAlarm_Status_Completed = 1
eAlarm_Status_Disabled = 2

cICalProperty_ALARM_X_ALARMSTATUS_PENDING = "PENDING"
cICalProperty_ALARM_X_ALARMSTATUS_COMPLETED = "COMPLETED"
cICalProperty_ALARM_X_ALARMSTATUS_DISABLED = "DISABLED"

cICalParameter_ORGANIZER_X_IDENTITY = "X-MULBERRY-IDENTITY"
cICalParameter_ATTENDEE_X_NEEDS_ITIP = "X-MULBERRY-NEEDS-ITIP"
