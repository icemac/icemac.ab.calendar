import icemac.ab.calendar.testing
from datetime import date


class RecurrenceTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Testing ..recurrence.*"""

    recurrence_start = date(2013, 5, 3)
    interval_start = date(2014, 4, 1)
    interval_end = date(2014, 4, 30)

    def callFUT(self, adapter_name, date=recurrence_start,
                start=interval_start, end=interval_end):
        from icemac.ab.calendar.recurrence import get_recurrings
        return list(get_recurrings(date, adapter_name, start, end))

    def test_Weekly_fulfills_IRecurringDate_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRecurringDate
        from ..recurrence import Weekly
        self.assertTrue(verifyObject(IRecurringDate, Weekly(None)))

    def test_weekly_returns_all_dates_in_interval_for_same_weekday(self):
        self.assertEqual([date(2014, 4, 4),
                          date(2014, 4, 11),
                          date(2014, 4, 18),
                          date(2014, 4, 25)], self.callFUT('weekly'))
        self.assertEqual(self.recurrence_start.isoweekday(),
                         self.callFUT('weekly')[0].isoweekday())

    def test_weekly_interval_end_does_not_belong_to_interval(self):
        self.assertEqual(
            [],
            self.callFUT(
                'weekly', start=date(2014, 4, 24), end=date(2014, 4, 25)))

    def test_weekly_interval_start_belongs_to_interval(self):
        self.assertEqual(
            [date(2014, 4, 4)],
            self.callFUT(
                'weekly', start=date(2014, 4, 4), end=date(2014, 4, 5)))
