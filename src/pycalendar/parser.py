##
#    Copyright (c) 2011-2013 Cyrus Daboo. All rights reserved.
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

class ParserContext(object):
    """
    Ultimately want to have these states as per-object so we can pass a context down
    through the entire parse call chain so that we can use different error handling for
    different situations. For now though it is a module static.
    """

    (
        PARSER_ALLOW, # Pass the "suspect" data through to the object model
        PARSER_IGNORE, # Ignore the "suspect" data
        PARSER_FIX, # Fix (or if not possible ignore) the "suspect" data
        PARSER_RAISE, # Raise an exception
    ) = range(4)

    # Some clients escape ":" - fix
    INVALID_COLON_ESCAPE_SEQUENCE = PARSER_FIX

    # Other escape sequences - raise
    INVALID_ESCAPE_SEQUENCES = PARSER_RAISE

    # Some client generate empty lines in the body of the data
    BLANK_LINES_IN_DATA = PARSER_FIX

    # Some clients still generate vCard 2 parameter syntax
    VCARD_2_NO_PARAMETER_VALUES = PARSER_ALLOW

    # Use this to fix v2 BASE64 to v3 ENCODING=b - only PARSER_FIX or PARSER_ALLOW
    VCARD_2_BASE64 = PARSER_FIX

    # Allow DATE values when DATETIME specified (and vice versa)
    INVALID_DATETIME_VALUE = PARSER_FIX

    # Allow slightly invalid DURATION values
    INVALID_DURATION_VALUE = PARSER_FIX

    # Truncate over long ADR and N values
    INVALID_ADR_N_VALUES = PARSER_FIX

    # REQUEST-STATUS values with \; as the first separator or single element
    INVALID_REQUEST_STATUS_VALUE = PARSER_FIX

    # Remove \-escaping in URI values when parsing - only PARSER_FIX or PARSER_ALLOW
    BACKSLASH_IN_URI_VALUE = PARSER_FIX

    @staticmethod
    def allRaise():
        """
        Make all tests raise an error - never fix
        """
        ParserContext.INVALID_COLON_ESCAPE_SEQUENCE = ParserContext.PARSER_RAISE
        ParserContext.INVALID_ESCAPE_SEQUENCES = ParserContext.PARSER_RAISE
        ParserContext.BLANK_LINES_IN_DATA = ParserContext.PARSER_RAISE
        ParserContext.VCARD_2_NO_PARAMETER_VALUES = ParserContext.PARSER_RAISE
        ParserContext.VCARD_2_BASE64 = ParserContext.PARSER_RAISE
        ParserContext.INVALID_DURATION_VALUE = ParserContext.PARSER_RAISE
        ParserContext.INVALID_ADR_N_VALUES = ParserContext.PARSER_RAISE
        ParserContext.INVALID_REQUEST_STATUS_VALUE = ParserContext.PARSER_RAISE
        ParserContext.BACKSLASH_IN_URI_VALUE = ParserContext.PARSER_RAISE
        ParserContext.INVALID_REQUEST_STATUS = ParserContext.PARSER_RAISE
