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

#from PyCalendarDateTime import PyCalendarDateTime

def readFoldedLine( ins, lines ):
    fail = False

    # If line2 already has data, transfer that into line1
    if len( lines[1] ) != 0:
        lines[0] = lines[1]
    else:
        # Fill first line
        try:
            lines[0] = ins.readline()
            if lines[0][-1] == "\n":
                lines[0] = lines[0][:-1]
            if lines[0][-1] == "\r":
                lines[0] = lines[0][:-1]
        except:
            fail = True

        if ( fail or ( lines[0] == 0 ) or ( len( lines[0] ) == 0 ) ):
            return False
 
    # Now loop looking ahead at the next line to see if it is folded
    while True:
        # Get next line
        try:
            lines[1] = ins.readline()
            if lines[1][-1] == "\n":
                lines[1] = lines[1][:-1]
            if lines[1][-1] == "\r":
                lines[1] = lines[1][:-1]
        except:
            fail = True

        if fail or ( lines[1] == 0 ):
            return True

        # Does it start with a space => folded
        if ( len( lines[1] ) != 0 ) and lines[1][0].isspace():
            # Copy folded line (without space) to current line and cycle
            # for more
            lines[0] = lines[0] + lines[1][1:]
        else:
            # Not folded - just exit loop
            break

    return True

def find_first_of( text, tokens, offset ):
    for i in range( offset, len( text ) ):
        if tokens.find( text[i] ) != -1:
            return i
    return -1
    
def writeTextValue( os, value ):
    try:
        start_pos = 0
        end_pos = find_first_of( value, "\r\n;\\,", start_pos )
        if end_pos != -1:
            while True:
                # Write current segment
                os.write( value[start_pos:end_pos] )

                # Write escape
                os.write("\\")
                c = value[end_pos]
                if c == '\r':
                    os.write("r")
                elif c == '\n':
                    os.write("n")
                elif c == ';':
                    os.write(";")
                elif c == '\\':
                    os.write("\\")
                elif c == ',':
                    os.write(",")

                # Bump past escapee and look for next segment
                start_pos = end_pos + 1

                end_pos = find_first_of(value, "\r\n;\\,", start_pos)
                if end_pos == -1:
                    os.write(value[start_pos:])
                    break
        else:
            os.write(value)
    
    except:
        pass
    
def decodeTextValue(value):
    os = StringIO.StringIO()

    start_pos = 0
    end_pos = find_first_of(value, "\\", start_pos)
    size_pos = len(value)
    if end_pos != -1:
        while True:
            # Write current segment upto but not including the escape char
            os.write(value[start_pos:end_pos])

            # Bump to escapee char but not past the end
            end_pos += 1
            if end_pos >= size_pos:
                break

            # Unescape
            c = value[end_pos]
            if c == 'r':
                os.write('\r')
            elif c == 'n':
                os.write('\n')
            elif c == '':
                os.write('')
            elif c == '\\':
                os.write('\\')
            elif c == ',':
                os.write(',')

            # Bump past escapee and look for next segment (not past the
            # end)
            start_pos = end_pos + 1
            if start_pos >= size_pos:
                break

            end_pos = find_first_of(value, "\\", start_pos)
            if end_pos == -1:
                os.write(value[start_pos:])
                break

    else:
        os.write(value)

    return os.getvalue()

# Date/time calcs
days_in_month      = ( 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 )
days_in_month_leap = ( 0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 )

def daysInMonth(month, year):
    # NB month is 1..12 so use dummy value at start of array to avoid index
    # adjustment
    if isLeapYear(year):
        return days_in_month_leap[month]
    else:
        return days_in_month[month]

days_upto_month      = ( 0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334 )
days_upto_month_leap = ( 0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335 )

def daysUptoMonth(month, year):
    # NB month is 1..12 so use dummy value at start of array to avoid index
    # adjustment
    if isLeapYear(year):
        return days_upto_month_leap[month]
    else:
        return days_upto_month[month]

def isLeapYear(year):
    if year <= 1752:
        return (year % 4 == 0)
    else:
        return ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0)

def leapDaysSince1970(year_offset):
    if year_offset > 2:
        return (year_offset + 1) / 4
    elif year_offset < -1:
        return (year_offset - 2) / 4
    else:
        return 0

#    public static int getLocalTimezoneOffsetSeconds() {
#        Calendar rightNow = Calendar.getInstance()
#        int tzoffset = rightNow.get(Calendar.ZONE_OFFSET)
#        int dstoffset = rightNow.get(Calendar.DST_OFFSET)
#        return -(tzoffset + dstoffset) / 1000
#    }

    # Packed date
def packDate(year, month, day):
    return (year << 16) | (month << 8) | (day + 128)

def unpackDate(data, unpacked):
    unpacked[0] = (data & 0xFFFF0000) >> 16
    unpacked[1] = (data & 0x0000FF00) >> 8
    unpacked[2] = (data & 0xFF) - 128

def unpackDateYear(data):
    return (data & 0xFFFF0000) >> 16

def unpackDateMonth(data):
    return (data & 0x0000FF00) >> 8

def unpackDateDay(data):
    return (data & 0xFF) - 128

# Display elements

def getMonthTable(month, year, weekstart, table, today_index):
    from pycalendar.datetime import PyCalendarDateTime

    # Get today
    today = PyCalendarDateTime.getToday(None)
    today_index = [-1, -1]

    # Start with empty table
    table = []

    # Determine first weekday in month
    temp = PyCalendarDateTime(year, month, 1, 0)
    row = -1
    initial_col = temp.getDayOfWeek() - weekstart
    if initial_col < 0:
        initial_col += 7
    col = initial_col

    # Counters
    max_day = daysInMonth(month, year)

    # Fill up each row
    for day in range( 1, max_day + 1):
        # Insert new row if we are at the start of a row
        if (col == 0) or (day == 1):
            row_data = []
            for i in range(0, 7):
                row_data.extend(0)
            table.extend(row_data)
            row += 1

        # Set the table item to the curret day
        table[row][col] = packDate(temp.getYear(), temp.getMonth(), day)

        # Check on today
        if (temp.getYear() == today.getYear()) and (temp.getMonth() == today.getMonth()) and (day == today.getDay()):
            today_index = [row, col]

        # Bump column (modulo 7)
        col += 1
        if (col > 6):
            col = 0

    # Add next month to remainder
    temp.offsetMonth(1)
    if col != 0:
        day = 1
        while col < 7:
            table[row][col] = packDate(temp.getYear(), temp.getMonth(), -day)

            # Check on today
            if (temp.getYear() == today.getYear()) and (temp.getMonth() == today.getMonth()) and (day == today.getDay()):
                today_index = [row, col]
                                                 
            day += 1
            col += 1

    # Add previous month to start
    temp.offsetMonth(-2)
    if (initial_col != 0):
        day = daysInMonth(temp.getMonth(), temp.getYear())
        back_col = initial_col - 1
        while(back_col >= 0):
            table[row][back_col] = packDate(temp.getYear(), temp.getMonth(), -day)

            # Check on today
            if (temp.getYear() == today.getYear()) and (temp.getMonth() == today.getMonth()) and (day == today.getDay()):
                today_index = [0, back_col]
                                                              
            back_col -= 1
            day -= 1

def set_difference(v1, v2):
    if len(v1) == 0 or len(v2) == 0:
        return v1

    s1 = set(v1)
    s2 = set(v2)
    s3 = s1.difference(s2)
    return list(s3)