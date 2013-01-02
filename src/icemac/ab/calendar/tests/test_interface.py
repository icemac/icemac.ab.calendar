# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt

import unittest
import zope.interface.verify
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.calendar


class TestInterfaces(unittest.TestCase):

    def test_calendar(self):
        zope.interface.verify.verifyObject(
            icemac.ab.calendar.interfaces.ICalendar,
            icemac.ab.calendar.calendar.Calendar())
