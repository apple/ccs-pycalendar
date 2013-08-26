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

from pycalendar import stringutils
from pycalendar.parameter import Parameter
from pycalendar.datetime import DateTime
from pycalendar.exceptions import InvalidProperty
from pycalendar.parser import ParserContext
from pycalendar.property import PropertyBase
from pycalendar.utcoffsetvalue import UTCOffsetValue
from pycalendar.utils import decodeParameterValue
from pycalendar.value import Value
from pycalendar.vcard import definitions
from pycalendar.vcard.adr import Adr
from pycalendar.vcard.adrvalue import AdrValue
from pycalendar.vcard.n import N
from pycalendar.vcard.nvalue import NValue
from pycalendar.vcard.orgvalue import OrgValue
import cStringIO as StringIO

handleOptions = ("allow", "ignore", "fix", "raise")
missingParameterValues = "fix"

class Property(PropertyBase):

    sDefaultValueTypeMap = {

        #     2425 Properties
        definitions.Property_SOURCE  : Value.VALUETYPE_URI,
        definitions.Property_NAME    : Value.VALUETYPE_TEXT,
        definitions.Property_PROFILE : Value.VALUETYPE_TEXT,

        #     2426 vCard Properties

        #     2426 Section 3.1
        definitions.Property_FN       : Value.VALUETYPE_TEXT,
        definitions.Property_N        : Value.VALUETYPE_TEXT,
        definitions.Property_NICKNAME : Value.VALUETYPE_TEXT,
        definitions.Property_PHOTO    : Value.VALUETYPE_BINARY,
        definitions.Property_BDAY     : Value.VALUETYPE_DATE,

        #     2426 Section 3.2
        definitions.Property_ADR   : Value.VALUETYPE_TEXT,
        definitions.Property_LABEL : Value.VALUETYPE_TEXT,

        #     2426 Section 3.3
        definitions.Property_TEL    : Value.VALUETYPE_TEXT,
        definitions.Property_EMAIL  : Value.VALUETYPE_TEXT,
        definitions.Property_MAILER : Value.VALUETYPE_TEXT,

        #     2426 Section 3.4
        definitions.Property_TZ  : Value.VALUETYPE_UTC_OFFSET,
        definitions.Property_GEO : Value.VALUETYPE_FLOAT,

        #     2426 Section 3.5
        definitions.Property_TITLE : Value.VALUETYPE_TEXT,
        definitions.Property_ROLE  : Value.VALUETYPE_TEXT,
        definitions.Property_LOGO  : Value.VALUETYPE_BINARY,
        definitions.Property_AGENT : Value.VALUETYPE_VCARD,
        definitions.Property_ORG   : Value.VALUETYPE_TEXT,

        #     2426 Section 3.6
        definitions.Property_CATEGORIES  : Value.VALUETYPE_TEXT,
        definitions.Property_NOTE        : Value.VALUETYPE_TEXT,
        definitions.Property_PRODID      : Value.VALUETYPE_TEXT,
        definitions.Property_REV         : Value.VALUETYPE_DATETIME,
        definitions.Property_SORT_STRING : Value.VALUETYPE_TEXT,
        definitions.Property_SOUND       : Value.VALUETYPE_BINARY,
        definitions.Property_UID         : Value.VALUETYPE_TEXT,
        definitions.Property_URL         : Value.VALUETYPE_URI,
        definitions.Property_VERSION     : Value.VALUETYPE_TEXT,

        #     2426 Section 3.7
        definitions.Property_CLASS       : Value.VALUETYPE_TEXT,
        definitions.Property_KEY         : Value.VALUETYPE_BINARY,
    }

    sValueTypeMap = {
        definitions.Value_BINARY      : Value.VALUETYPE_BINARY,
        definitions.Value_BOOLEAN     : Value.VALUETYPE_BOOLEAN,
        definitions.Value_DATE        : Value.VALUETYPE_DATE,
        definitions.Value_DATE_TIME   : Value.VALUETYPE_DATETIME,
        definitions.Value_FLOAT       : Value.VALUETYPE_FLOAT,
        definitions.Value_INTEGER     : Value.VALUETYPE_INTEGER,
        definitions.Value_TEXT        : Value.VALUETYPE_TEXT,
        definitions.Value_TIME        : Value.VALUETYPE_TIME,
        definitions.Value_URI         : Value.VALUETYPE_URI,
        definitions.Value_UTCOFFSET   : Value.VALUETYPE_UTC_OFFSET,
        definitions.Value_VCARD       : Value.VALUETYPE_VCARD,
    }

    sTypeValueMap = {
        Value.VALUETYPE_ADR        : definitions.Value_TEXT,
        Value.VALUETYPE_BINARY     : definitions.Value_BINARY,
        Value.VALUETYPE_BOOLEAN    : definitions.Value_BOOLEAN,
        Value.VALUETYPE_DATE       : definitions.Value_DATE,
        Value.VALUETYPE_DATETIME   : definitions.Value_DATE_TIME,
        Value.VALUETYPE_FLOAT      : definitions.Value_FLOAT,
        Value.VALUETYPE_GEO        : definitions.Value_FLOAT,
        Value.VALUETYPE_INTEGER    : definitions.Value_INTEGER,
        Value.VALUETYPE_N          : definitions.Value_TEXT,
        Value.VALUETYPE_ORG        : definitions.Value_TEXT,
        Value.VALUETYPE_TEXT       : definitions.Value_TEXT,
        Value.VALUETYPE_TIME       : definitions.Value_TIME,
        Value.VALUETYPE_URI        : definitions.Value_URI,
        Value.VALUETYPE_UTC_OFFSET : definitions.Value_UTCOFFSET,
        Value.VALUETYPE_VCARD      : definitions.Value_VCARD,
    }

    sMultiValues = set((
        definitions.Property_NICKNAME,
        definitions.Property_CATEGORIES,
    ))

    sSpecialVariants = {
        definitions.Property_ADR : Value.VALUETYPE_ADR,
        definitions.Property_GEO : Value.VALUETYPE_GEO,
        definitions.Property_N: Value.VALUETYPE_N,
        definitions.Property_ORG: Value.VALUETYPE_ORG,
    }

    sUsesGroup = True

    sVariant = "vcard"

    sValue = definitions.Parameter_VALUE
    sText = definitions.Value_TEXT

    def __init__(self, group=None, name=None, value=None, valuetype=None):

        super(Property, self).__init__(name, value, valuetype)

        self.mGroup = group

        # The None check speeds up .duplicate()
        if value is None:
            pass

        if isinstance(value, int):
            self._init_attr_value_int(value)

        elif isinstance(value, str):
            self._init_attr_value_text(value, valuetype if valuetype else self.sDefaultValueTypeMap.get(self.mName.upper(), Value.VALUETYPE_TEXT))

        elif isinstance(value, DateTime):
            self._init_attr_value_datetime(value)

        elif isinstance(value, Adr):
            self._init_attr_value_adr(value)

        elif isinstance(value, N):
            self._init_attr_value_n(value)

        elif isinstance(value, list) or isinstance(value, tuple):
            if name.upper() == definitions.Property_ORG:
                self._init_attr_value_org(value)
            elif name.upper() == definitions.Property_GEO:
                self._init_attr_value_geo(value)
            else:
                # Assume everything else is a text list
                self._init_attr_value_text_list(value)

        elif isinstance(value, UTCOffsetValue):
            self._init_attr_value_utcoffset(value)


    def duplicate(self):
        other = Property(self.mGroup, self.mName)
        for attrname, attrs in self.mParameters.items():
            other.mParameters[attrname] = [i.duplicate() for i in attrs]
        other.mValue = self.mValue.duplicate()

        return other


    def __hash__(self):
        return hash((
            self.mGroup,
            self.mName,
            tuple([tuple(self.mParameters[attrname]) for attrname in sorted(self.mParameters.keys())]),
            self.mValue,
        ))


    def __eq__(self, other):
        if not isinstance(other, Property):
            return False
        return (
            self.mGroup == self.mGroup and
            self.mName == other.mName and
            self.mValue == other.mValue and
            self.mParameters == other.mParameters
        )


    def parseTextParameters(self, txt, data):
        """
        Parse parameters, return string point at value.
        """

        try:
            stripValueSpaces = False    # Fix for AB.app base PHOTO properties that use two spaces at start of line
            while txt:
                if txt[0] == ';':
                    # Parse parameter

                    # Move past delimiter
                    txt = txt[1:]

                    # Get quoted string or token - in iCalendar we only look for "=" here
                    # but for "broken" vCard BASE64 property we need to also terminate on
                    # ":;"
                    parameter_name, txt = stringutils.strduptokenstr(txt, "=:;")
                    if parameter_name is None:
                        raise InvalidProperty("Invalid property", data)

                    if txt[0] != "=":
                        # Deal with parameters without values
                        if ParserContext.VCARD_2_NO_PARAMETER_VALUES == ParserContext.PARSER_RAISE:
                            raise InvalidProperty("Invalid property parameter", data)
                        elif ParserContext.VCARD_2_NO_PARAMETER_VALUES == ParserContext.PARSER_ALLOW:
                            parameter_value = None
                        else: # PARSER_IGNORE and PARSER_FIX
                            parameter_name = None

                        if parameter_name.upper() == "BASE64" and ParserContext.VCARD_2_BASE64 == ParserContext.PARSER_FIX:
                            parameter_name = definitions.Parameter_ENCODING
                            parameter_value = definitions.Parameter_Value_ENCODING_B
                            stripValueSpaces = True
                    else:
                        txt = txt[1:]
                        parameter_value, txt = stringutils.strduptokenstr(txt, ":;,")
                        if parameter_value is None:
                            raise InvalidProperty("Invalid property", data)

                    # Now add parameter value (decode ^-escaping)
                    if parameter_name is not None:
                        attrvalue = Parameter(name=parameter_name, value=decodeParameterValue(parameter_value))
                        self.mParameters.setdefault(parameter_name.upper(), []).append(attrvalue)

                    # Look for additional values
                    while txt[0] == ',':
                        txt = txt[1:]
                        parameter_value2, txt = stringutils.strduptokenstr(txt, ":;,")
                        if parameter_value2 is None:
                            raise InvalidProperty("Invalid property", data)
                        attrvalue.addValue(decodeParameterValue(parameter_value2))
                elif txt[0] == ':':
                    txt = txt[1:]
                    if stripValueSpaces:
                        txt = txt.replace(" ", "")
                    return txt

        except IndexError:
            raise InvalidProperty("Invalid property", data)


    # Write out the actual property, possibly skipping the value
    def generateValue(self, os, novalue):

        # Special case AB.app PHOTO values
        if self.mName.upper() == "PHOTO" and self.mValue.getType() == Value.VALUETYPE_BINARY:
            self.setupValueParameter()

            # Must write to temp buffer and then wrap
            sout = StringIO.StringIO()
            if self.mGroup:
                sout.write(self.mGroup + ".")
            sout.write(self.mName)

            # Write all parameters
            for key in sorted(self.mParameters.keys()):
                for attr in self.mParameters[key]:
                    sout.write(";")
                    attr.generate(sout)

            # Write value
            sout.write(":")
            sout.write("\r\n")

            value = self.mValue.getText()
            value_len = len(value)
            offset = 0
            while(value_len > 72):
                sout.write(" ")
                sout.write(value[offset:offset + 72])
                sout.write("\r\n")
                value_len -= 72
                offset += 72
            sout.write(" ")
            sout.write(value[offset:])
            os.write(sout.getvalue())
            os.write("\r\n")
        else:
            super(Property, self).generateValue(os, novalue)


    # Creation
    def _init_attr_value_adr(self, reqstatus):
        # Value
        self.mValue = AdrValue(reqstatus)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_n(self, reqstatus):
        # Value
        self.mValue = NValue(reqstatus)

        # Parameters
        self.setupValueParameter()


    def _init_attr_value_org(self, reqstatus):
        # Value
        self.mValue = OrgValue(reqstatus)

        # Parameters
        self.setupValueParameter()
