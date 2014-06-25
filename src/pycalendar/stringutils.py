##
#    Copyright (c) 2007-2013 Cyrus Daboo. All rights reserved.
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

from hashlib import md5

def strduptokenstr(txt, tokens):

    # First punt over any leading space - this is not common so test the
    # first character before trying the more expensive strip
    if txt[0] == " ":
        txt = txt.lstrip()
        if not txt:
            return None, ""

    # Handle quoted string
    if txt[0] == '\"':
        skip = False
        for end, s in enumerate(txt[1:]):
            if skip:
                skip = False
                continue
            elif s == '\"':
                return txt[1:end + 1], txt[end + 2:]
            else:
                skip = (s == '\\')
        else:
            return None, txt
    else:
        for end, s in enumerate(txt):
            if s in tokens:
                return txt[0:end], txt[end:]
        return txt, ""



def strtoul(s, offset=0):

    max = len(s)
    startoffset = offset
    while offset < max:
        if s[offset] in "0123456789":
            offset += 1
            continue
        elif offset == 0:
            raise ValueError
        else:
            return int(s[startoffset:offset]), offset
    else:
        if offset == 0:
            raise ValueError
        else:
            return int(s[startoffset:]), offset



def strindexfind(s, ss, default_index):
    if s and ss:
        i = 0
        s = s.upper()
        while ss[i]:
            if s == ss[i]:
                return i
            i += 1

    return default_index



def strnindexfind(s, ss, default_index):
    if s and ss:
        i = 0
        s = s.upper()
        while ss[i]:
            if s.startswith(ss[i]):
                return i
            i += 1

    return default_index



def compareStringsSafe(s1, s2):
    if s1 is None and s2 is None:
        return True
    elif (s1 is None and s2 is not None) or (s1 is not None and s2 is None):
        return False
    else:
        return s1 == s2



def md5digest(txt):
    return md5.new(txt).hexdigest()
