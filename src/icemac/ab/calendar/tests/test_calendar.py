# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import unittest
import icemac.ab.calendar.testing


class CalendarUTests(unittest.TestCase):
    """Unit testing ..calendar.Calendar."""

    def test_calendar_implements_ICalendar_interface(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.interfaces import ICalendar
        from icemac.ab.calendar.calendar import Calendar

        self.assertTrue(verifyObject(ICalendar, Calendar()))


class Calendar_get_events_FTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Functional testing ..calendar.Calendar.get_events()"""

    def setUp(self):
        from datetime import datetime
        from pytz import utc
        super(Calendar_get_events_FTests, self).setUp()
        self.create_event(alternative_title=u'end Jan 2013',
                          datetime=datetime(2013, 1, 31, 23, 59, tzinfo=utc))
        self.create_event(alternative_title=u'start Feb 2013',
                          datetime=datetime(2013, 2, 1, 0, tzinfo=utc))
        self.create_event(alternative_title=u'end Feb 2013',
                          datetime=datetime(2013, 2, 28, 23, 59, tzinfo=utc))
        self.create_event(alternative_title=u'start Mar 2013',
                          datetime=datetime(2013, 3, 1, 0, tzinfo=utc))

    def callMUT(self, month, year, timezone=None):
        from gocept.month import Month
        import pytz
        calendar = self.layer['addressbook'].calendar
        if timezone is not None:
            timezone = pytz.timezone(timezone)
        events = calendar.get_events(Month(month, year), timezone=timezone)
        return [x.alternative_title for x in events]

    def test_returns_only_events_in_month(self):
        self.assertEqual([u'start Feb 2013', u'end Feb 2013'],
                         self.callMUT(2, 2013))

    def test_respects_the_given_time_eastern_zone(self):
        self.assertEqual([u'end Feb 2013', 'start Mar 2013'],
                         self.callMUT(2, 2013, 'Etc/GMT+1'))

    def test_respects_the_given_time_western_zone(self):
        self.assertEqual([u'end Jan 2013', 'start Feb 2013'],
                         self.callMUT(2, 2013, 'Etc/GMT-1'))
