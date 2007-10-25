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

import md5

def strduptokenstr(txt, tokens):
    
    result = None
    start = 0

    # First punt over any leading space
    maxlen = len(txt)
    while (start < maxlen) and (txt[start] == ' '):
        start += 1
    if start == maxlen:
        return None, ""

    # Handle quoted string
    if txt[start] == '\"':
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

        result = txt[start:end]
        txt = txt[end + 1:]

        return result, txt
    else:
        end = start
        for end in range(end, maxlen): #@UnusedVariable
            if tokens.find(txt[end]) != -1:
                # Grab portion of string upto delimiter
                if end > start:
                    result = txt[start:end]
                else:
                    result = ""
                txt = txt[end:]
                return result, txt

        result = txt[start:]
        txt = ""

        return result, txt

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
