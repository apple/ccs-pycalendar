##
#    Copyright (c) 2011-2012 Cyrus Daboo. All rights reserved.
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

from pycalendar.n import N
import unittest

class TestAdrValue(unittest.TestCase):

    def testInit(self):

        data = (
            (
                ("last", "first", "middle", "prefix", "suffix"),
                "last;first;middle;prefix;suffix",
                "prefix first middle last suffix",
            ),
            (
                ("last", ("first",), ("middle1", "middle2",), (), ("suffix",)),
                "last;first;middle1,middle2;;suffix",
                "first middle1 middle2 last suffix",
            ),
        )

        for args, result, fullName in data:
            n = N(*args)

            self.assertEqual(
                n.getValue(),
                args,
            )

            self.assertEqual(
                n.getText(),
                result,
            )

            self.assertEqual(
                n.getFullName(),
                fullName,
            )

            self.assertEqual(
                n.duplicate().getText(),
                result,
            )


    def testInitWithKeywords(self):

        data = (
            (
                {"first": "first", "last": "last", "middle": "middle", "prefix": "prefix", "suffix": "suffix"},
                "last;first;middle;prefix;suffix",
                "prefix first middle last suffix",
            ),
            (
                {"first": ("first",), "last": "last", "middle": ("middle1", "middle2",), "prefix": (), "suffix": ("suffix",)},
                "last;first;middle1,middle2;;suffix",
                "first middle1 middle2 last suffix",
            ),
        )

        for kwargs, result, fullName in data:
            n = N(**kwargs)

            self.assertEqual(
                n.getText(),
                result,
            )

            self.assertEqual(
                n.getFullName(),
                fullName,
            )

            self.assertEqual(
                n.duplicate().getText(),
                result,
            )
