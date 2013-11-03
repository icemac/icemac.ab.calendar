import unittest


class CalendarUTests(unittest.TestCase):
    """Unit testing ..base.Calendar."""

    def test_Calendar_fulfills_IRenderer_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRenderer
        from ..base import Calendar
        self.assertTrue(verifyObject(IRenderer, Calendar(None, None, None)))
