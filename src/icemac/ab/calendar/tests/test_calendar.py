# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import unittest


class CalendarTests(unittest.TestCase):
    """Testing ..calendar.Calendar."""

    def test_calendar_implements_ICalendar_interface(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.interfaces import ICalendar
        from icemac.ab.calendar.calendar import Calendar

        self.assertTrue(verifyObject(ICalendar, Calendar()))
