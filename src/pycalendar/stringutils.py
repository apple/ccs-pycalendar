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

    result = None
    start = 0

    # First punt over any leading space
    for s in txt:
        if s == " ":
            start += 1
        else:
            break
    else:
        return None, ""

    # Handle quoted string
    if txt[start] == '\"':

        maxlen = len(txt)
        # Punt leading quote
        start += 1
        end = start

        done = False
        while not done:
            if end == maxlen:
                return None, txt

            if txt[end] == '\"':
                done = True
            elif txt[end] == '\\':
                # Punt past quote
                end += 2
            else:
                end += 1
            if end >= maxlen:
                return None, txt

        return txt[start:end], txt[end + 1:]
    else:
        for relend, s in enumerate(txt[start:]):
            if s in tokens:
                if relend:
                    result = txt[start:start + relend]
                else:
                    result = ""
                return result, txt[start + relend:]
        return txt[start:], ""



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
