# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
import unittest
import icemac.ab.calendar.testing


class CalendarUTests(unittest.TestCase):
    """Unit testing ..calendar.*."""

    def test_calendar_fulfills_ICalendar_interface(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.interfaces import ICalendar
        from icemac.ab.calendar.calendar import Calendar

        self.assertTrue(verifyObject(ICalendar, Calendar()))

    def test_CalendarDisplaySettings_fulfills_ICalendarDisplaySettings(self):
        from zope.interface.verify import verifyObject
        from icemac.ab.calendar.interfaces import ICalendarDisplaySettings
        from icemac.ab.calendar.calendar import CalendarDisplaySettings

        self.assertTrue(
            verifyObject(ICalendarDisplaySettings, CalendarDisplaySettings()))


class Calendar_get_events_FTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Functional testing ..calendar.Calendar.get_events()"""

    def setUp(self):
        super(Calendar_get_events_FTests, self).setUp()
        # Order of creation is important to test that the results are sorted:
        self.create_event(alternative_title=u'start Mar 2013',
                          datetime=self.get_datetime((2013, 3, 1, 0)))
        self.create_event(alternative_title=u'start Feb 2013',
                          datetime=self.get_datetime((2013, 2, 1, 0)))
        self.create_event(alternative_title=u'end Jan 2013',
                          datetime=self.get_datetime((2013, 1, 31, 23, 59)))
        self.create_event(alternative_title=u'end Feb 2013',
                          datetime=self.get_datetime((2013, 2, 28, 23, 59)))

    def callMUT(self, month, year, timezone=None, show_date=False):
        from gocept.month import Month
        calendar = self.layer['addressbook'].calendar
        events = calendar.get_events(Month(month, year), timezone=timezone)
        if show_date:
            return [(x.alternative_title, x.datetime.date().isoformat())
                    for x in events]
        return [x.alternative_title for x in events]

    def test_returns_only_events_in_month(self):
        self.assertEqual([u'start Feb 2013', u'end Feb 2013'],
                         self.callMUT(2, 2013))

    def test_respects_the_given_time_eastern_zone(self):
        self.assertEqual([u'end Feb 2013', u'start Mar 2013'],
                         self.callMUT(2, 2013, 'Etc/GMT+1'))

    def test_respects_the_given_time_western_zone(self):
        self.assertEqual([u'end Jan 2013', u'start Feb 2013'],
                         self.callMUT(2, 2013, 'Etc/GMT-1'))

    def test_returns_recurring_events_in_month(self):
        self.create_recurring_event(
            alternative_title=u'each week',
            datetime=self.get_datetime((2013, 2, 14, 23, 0)),
            period=u'weekly',
            category=self.create_category(u'night lunch'))
        self.create_recurring_event(
            alternative_title=u'each week in future',
            datetime=self.get_datetime((2013, 3, 1, 0)),
            period=u'weekly',
            category=self.create_category(u'midnight'))
        self.assertEqual([(u'end Jan 2013', '2013-01-31'),
                          (u'start Feb 2013', '2013-02-01'),
                          (u'each week', '2013-02-14'),
                          (u'each week', '2013-02-21')],
                         self.callMUT(2, 2013, 'Etc/GMT-1', show_date=True))

    def test_customized_recurred_event_hides_recurred_event(self):
        from icemac.ab.calendar.event import (
            get_event_data_from_recurring_event)
        night_lunch = self.create_category(u'night lunch')
        recurring_event = self.create_recurring_event(
            alternative_title=u'each week',
            datetime=self.get_datetime((2013, 3, 14, 23, 0)),
            period=u'weekly',
            category=night_lunch)
        event_data = get_event_data_from_recurring_event(
            recurring_event, self.get_datetime((2013, 3, 21, 0)).date())
        event_data['alternative_title'] = u'this week'
        self.create_event(**event_data)
        self.assertEqual([(u'each week', '2013-03-14'),
                          (u'this week', '2013-03-21'),
                          (u'each week', '2013-03-28')],
                         self.callMUT(3, 2013, 'Etc/GMT+1', show_date=True))

    def test_does_not_return_deleted_events(self):
        self.create_event(
            alternative_title=u'deleted start of March 2013',
            datetime=self.get_datetime((2013, 3, 1, 5)),
            deleted=True)
        self.assertEqual([u'start Mar 2013'],
                         self.callMUT(3, 2013, 'Etc/GMT'))


class CalendarDisplaySettingsTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..calendar.CalendarDisplaySettings."""

    def setUp(self):
        from icemac.addressbook.testing import create_field
        from icemac.addressbook.interfaces import IEntity
        from icemac.ab.calendar.interfaces import IEvent
        super(CalendarDisplaySettingsTests, self).setUp()
        user_field_name = create_field(
            self.layer['addressbook'], IEvent, 'Int', u'Num')
        self.user_field = IEntity(IEvent).getRawField(user_field_name)

    def getCUT(self):
        from ..calendar import CalendarDisplaySettings
        return CalendarDisplaySettings()

    def test_event_additional_fields_stores_string_repr_of_fields(self):
        from ..interfaces import IEvent
        cds = self.getCUT()
        cds.event_additional_fields = [IEvent['text'], self.user_field]
        self.assertEqual(['IcemacAbCalendarEventEvent###text',
                          'IcemacAbCalendarEventEvent###Field-1'],
                         cds._event_additional_fields)

    def test_event_additional_fields_returns_actual_fields(self):
        from ..interfaces import IEvent
        cds = self.getCUT()
        cds._event_additional_fields = ['IcemacAbCalendarEventEvent###text',
                                        'IcemacAbCalendarEventEvent###Field-1']
        self.assertEqual([IEvent['text'], self.user_field],
                         cds.event_additional_fields)
