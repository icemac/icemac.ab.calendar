# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import unittest


class EventTests(unittest.TestCase):
    """Testing ..event.Event."""

    def test_event_implements_IEvent_interface(self):
        from gocept.reference.verify import verifyObject
        from icemac.ab.calendar.interfaces import IEvent
        from icemac.ab.calendar.event import Event

        self.assertTrue(verifyObject(IEvent, Event()))
