import icemac.ab.calendar.testing
from datetime import date, datetime


class RecurrenceTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Testing ..recurrence.*"""

    recurrence_start = datetime(2013, 5, 3, 21, 45)
    interval_start = date(2014, 4, 1)
    interval_end = date(2014, 4, 30)

    def callFUT(self, adapter_name, date=recurrence_start,
                start=interval_start, end=interval_end):
        from icemac.ab.calendar.recurrence import get_recurrings
        return list(get_recurrings(date, adapter_name, start, end))

    def test_Weekly_fulfills_IRecurringDateTime_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRecurringDateTime
        from ..recurrence import Weekly
        self.assertTrue(verifyObject(IRecurringDateTime, Weekly(None)))

    def test_weekly_returns_all_dates_in_interval_for_same_weekday(self):
        self.assertEqual(
            [datetime(2014, 4, 4, 21, 45),
             datetime(2014, 4, 11, 21, 45),
             datetime(2014, 4, 18, 21, 45),
             datetime(2014, 4, 25, 21, 45)], self.callFUT('weekly'))
        self.assertEqual(self.recurrence_start.isoweekday(),
                         self.callFUT('weekly')[0].isoweekday())

    def test_weekly_interval_end_does_not_belong_to_interval(self):
        self.assertEqual(
            [],
            self.callFUT(
                'weekly', start=date(2014, 4, 24), end=date(2014, 4, 25)))

    def test_weekly_interval_start_belongs_to_interval(self):
        self.assertEqual(
            [datetime(2014, 4, 4, 21, 45)],
            self.callFUT(
                'weekly', start=date(2014, 4, 4), end=date(2014, 4, 5)))
