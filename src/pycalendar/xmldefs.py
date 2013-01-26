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

import xml.etree.cElementTree as XML

# iCalendar/vCard XML definitions

iCalendar20_namespace = "urn:ietf:params:xml:ns:icalendar-2.0"

icalendar = "icalendar"
components = "components"
properties = "properties"
parameters = "parameters"

value_binary = "binary"
value_boolean = "boolean"
value_cal_address = "cal-address"
value_date = "date"
value_date_time = "date-time"
value_duration = "duration"
value_integer = "integer"
value_period = "period"
value_recur = "recur"
value_text = "text"
value_unknown = "unknown"
value_uri = "uri"
value_utc_offset = "utc-offset"

period_start = "start"
period_end = "end"
period_duration = "duration"

recur_freq = "freq"
recur_freq_secondly = "SECONDLY"
recur_freq_minutely = "MINUTELY"
recur_freq_hourly = "HOURLY"
recur_freq_daily = "DAILY"
recur_freq_weekly = "WEEKLY"
recur_freq_monthly = "MONTHLY"
recur_freq_yearly = "YEARLY"

recur_count = "count"
recur_until = "until"
recur_interval = "interval"

recur_bysecond = "bysecond"
recur_byminute = "byminute"
recur_byhour = "byhour"
recur_byday = "byday"
recur_bymonthday = "bymonthday"
recur_byyearday = "byyearday"
recur_byweekno = "byweekno"
recur_bymonth = "bymonth"
recur_bysetpos = "bysetpos"
recur_wkst = "wkst"

req_status_code = "code"
req_status_description = "description"
req_status_data = "data"

vCard40_namespace = "urn:ietf:params:xml:ns:vcard-4.0"

def makeTag(namespace, name):
    return "{%s}%s" % (namespace, name.lower(),)



def toString(root):

    data = """<?xml version="1.0" encoding="utf-8"?>\n"""

    INDENT = 2

    # Generate indentation
    def _indentNode(node, level=0):

        if node.text is not None and node.text.strip():
            return
        elif len(node.getchildren()):
            indent = "\n" + " " * (level + 1) * INDENT
            node.text = indent
            for child in node.getchildren():
                child.tail = indent
                _indentNode(child, level + 1)
            if len(node.getchildren()):
                node.getchildren()[-1].tail = "\n" + " " * level * INDENT

    _indentNode(root, 0)
    data += XML.tostring(root) + "\n"

    return data
