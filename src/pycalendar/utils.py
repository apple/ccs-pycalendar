##
#    Copyright (c) 2007-2011 Cyrus Daboo. All rights reserved.
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

from pycalendar.parser import ParserContext
import cStringIO as StringIO

def readFoldedLine( ins, lines ):

    # If line2 already has data, transfer that into line1
    if lines[1] is not None:
        lines[0] = lines[1]
    else:
        # Fill first line
        try:
            myline = ins.readline()
            if len(myline) == 0:
                raise ValueError
            if myline[-1] == "\n":
                if myline[-2] == "\r":
                    lines[0] = myline[:-2]
                else:
                    lines[0] = myline[:-1]
            elif myline[-1] == "\r":
                lines[0] = myline[:-1]
            else:
                lines[0] = myline
        except IndexError:
            lines[0] = ""
        except:
            lines[0] = None
            return False
 
    # Now loop looking ahead at the next line to see if it is folded
    while True:
        # Get next line
        try:
            myline = ins.readline()
            if len(myline) == 0:
                raise ValueError
            if myline[-1] == "\n":
                if myline[-2] == "\r":
                    lines[1] = myline[:-2]
                else:
                    lines[1] = myline[:-1]
            elif myline[-1] == "\r":
                lines[1] = myline[:-1]
            else:
                lines[1] = myline
        except IndexError:
            lines[1] = ""
        except:
            lines[1] = None
            return True

        if not lines[1]:
            return True

        # Does it start with a space => folded
        if lines[1][0].isspace():
            # Copy folded line (without space) to current line and cycle
            # for more
            lines[0] = lines[0] + lines[1][1:]
        else:
            # Not folded - just exit loop
            break

    return True

def find_first_of( text, tokens, offset ):
    for ctr, c in enumerate(text[offset:]):
        if c in tokens:
            return offset + ctr
    return -1

def escapeTextValue(value):
    os = StringIO.StringIO()
    writeTextValue(os, value)
    return os.getvalue()

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
            elif c == 'N':
                os.write('\n')
            elif c == '':
                os.write('')
            elif c == '\\':
                os.write('\\')
            elif c == ',':
                os.write(',')
            elif c == ';':
                os.write(';')
            elif c == ':':
                # ":" escape normally invalid
                if ParserContext.INVALID_COLON_ESCAPE_SEQUENCE == ParserContext.PARSER_RAISE:
                    raise ValueError
                elif ParserContext.INVALID_COLON_ESCAPE_SEQUENCE == ParserContext.PARSER_FIX:
                    os.write(':')
                    
            # Other escaped chars normally not allowed
            elif ParserContext.INVALID_ESCAPE_SEQUENCES == ParserContext.PARSER_RAISE:
                raise ValueError
            elif ParserContext.INVALID_ESCAPE_SEQUENCES == ParserContext.PARSER_FIX:
                os.write(c)

            # Bump past escapee and look for next segment (not past the end)
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

# vCard text list parsing/generation
def parseTextList(data, sep=';'):
    """
    Each element of the list has to be separately un-escaped
    """
    results = []
    item = []
    pre_s = ''
    for s in data:
        if s == sep and pre_s != '\\':
            results.append(decodeTextValue("".join(item)))
            item = []
        else:
            item.append(s)
        pre_s = s
    
    results.append(decodeTextValue("".join(item)))

    return tuple(results) if len(results) > 1 else (results[0] if len(results) else "")

def generateTextList(os, data, sep=';'):
    """
    Each element of the list must be separately escaped
    """
    try:
        if isinstance(data, basestring):
            data = (data,)
        results = [escapeTextValue(value) for value in data]
        os.write(sep.join(results))
    except:
        pass

# vCard double-nested list parsing/generation
def parseDoubleNestedList(data, maxsize):
    results = []
    items = [""]
    pre_s = ''
    for s in data:
        if s == ';' and pre_s != '\\':
            
            if len(items) > 1:
                results.append(tuple([decodeTextValue(item) for item in items]))
            elif len(items) == 1:
                results.append(decodeTextValue(items[0]))
            else:
                results.append("")
            
            items = [""]
        elif s == ',' and pre_s != '\\':
            items.append("")
        else:
            items[-1] += s
        pre_s = s
    
    if len(items) > 1:
        results.append(tuple([decodeTextValue(item) for item in items]))
    elif len(items) == 1:
        results.append(decodeTextValue(items[0]))
    else:
        results.append("")

    for _ignore in range(maxsize - len(results)):
        results.append("")

    if len(results) > maxsize:
        if ParserContext.INVALID_ADR_N_VALUES == ParserContext.PARSER_FIX:
            results = results[:maxsize]
        elif ParserContext.INVALID_ADR_N_VALUES == ParserContext.PARSER_RAISE:
            raise ValueError

    return tuple(results)

def generateDoubleNestedList(os, data):
    try:
        def _writeElement(item):
            if isinstance(item, basestring):
                writeTextValue(os, item)
            else:
                if item:
                    writeTextValue(os, item[0])
                    for bit in item[1:]:
                        os.write(",")
                        writeTextValue(os, bit)
            
        for item in data[:-1]:
            _writeElement(item)
            os.write(";")
        _writeElement(data[-1])
        
    except:
        pass

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

cachedLeapYears = {}
def isLeapYear(year):
    
    try:
        return cachedLeapYears[year]
    except KeyError:
        if year <= 1752:
            result = (year % 4 == 0)
        else:
            result = ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0)
        cachedLeapYears[year] = result
        return result

cachedLeapDaysSince1970 = {}
def leapDaysSince1970(year_offset):
    
    try:
        return cachedLeapDaysSince1970[year_offset]
    except KeyError:
        if year_offset > 2:
            result = (year_offset + 1) / 4
        elif year_offset < -1:
            # Python will round down negative numbers (i.e. -5/4 = -2, but we want -1), so
            # what is (year_offset - 2) in C code is actually (year_offset - 2 + 3) in Python.
            result = (year_offset + 1) / 4
        else:
            result = 0
        cachedLeapDaysSince1970[year_offset] = result
        return result

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
            table.extend([0] * 7)
            row += 1

        # Set the table item to the current day
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

    return table, today_index

def set_difference(v1, v2):
    if len(v1) == 0 or len(v2) == 0:
        return v1

    s1 = set(v1)
    s2 = set(v2)
    s3 = s1.difference(s2)
    return list(s3)