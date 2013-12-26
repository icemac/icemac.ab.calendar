# -*- coding: utf-8 -*-
import gocept.testing.assertion
import unittest


class CalendarUTests(unittest.TestCase,
                     gocept.testing.assertion.Exceptions):
    """Unit testing ..base.Calendar."""

    def _make_one(self):
        from ..base import Calendar
        return Calendar(None, None, None)

    def test_Calendar_fulfills_IRenderer_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRenderer
        from ..base import Calendar
        self.assertTrue(verifyObject(IRenderer, self._make_one()))

    def test_write_does_not_fail_on_non_ASCII_chars(self):
        calendar = self._make_one()
        with self.assertNothingRaised():
            calendar.write(u'aäöü%s', u'ßen')
        self.assertEqual(u'aäöüßen\n', calendar.read())
