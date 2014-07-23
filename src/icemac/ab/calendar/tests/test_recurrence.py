import icemac.ab.calendar.testing
import unittest


class RecurrenceMixIn(object):
    """Mix-in to test ..recurrence.*."""

    def setUp(self):
        super(RecurrenceMixIn, self).setUp()
        self.recurrence_start = self.get_datetime((2013, 5, 3, 21, 45))
        self.interval_start = self.get_datetime((2014, 4, 1))
        self.interval_end = self.get_datetime((2014, 4, 30))

    def callFUT(self, adapter_name, datetime=None, start=None, end=None):
        from icemac.ab.calendar.recurrence import get_recurrences
        datetime = self.recurrence_start if datetime is None else datetime
        start = self.interval_start if start is None else start
        end = self.interval_end if end is None else end
        return list(get_recurrences(datetime, adapter_name, start, end))


class WeeklyTests(RecurrenceMixIn, icemac.ab.calendar.testing.ZCMLTestCase):
    """Testing ..recurrence.Weekly"""

    def test_instance_fulfills_IRecurringDateTime_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRecurringDateTime
        from ..recurrence import Weekly
        self.assertTrue(verifyObject(IRecurringDateTime, Weekly(None)))

    def test_returns_all_dates_in_interval_for_same_weekday(self):
        self.assertEqual(
            [self.get_datetime((2014, 4, 4, 21, 45)),
             self.get_datetime((2014, 4, 11, 21, 45)),
             self.get_datetime((2014, 4, 18, 21, 45)),
             self.get_datetime((2014, 4, 25, 21, 45))], self.callFUT('weekly'))
        self.assertEqual(self.recurrence_start.isoweekday(),
                         self.callFUT('weekly')[0].isoweekday())

    def test_does_not_start_before_datetime(self):
        self.assertEqual(
            [self.get_datetime((2014, 4, 18, 21, 45)),
             self.get_datetime((2014, 4, 25, 21, 45))],
            self.callFUT('weekly',
                         datetime=self.get_datetime((2014, 4, 18, 21, 45))))
        self.assertEqual(self.recurrence_start.isoweekday(),
                         self.callFUT('weekly')[0].isoweekday())

    def test_returns_empty_interval_if_datetime_after_interval_end(self):
        self.assertEqual(
            [], self.callFUT(
                'weekly', datetime=self.get_datetime((2014, 5, 1, 21, 45))))

    def test_interval_end_does_not_belong_to_interval(self):
        self.assertEqual(
            [], self.callFUT(
                'weekly', start=self.get_datetime((2014, 4, 24)),
                end=self.get_datetime((2014, 4, 25))))

    def test_interval_start_belongs_to_interval(self):
        self.assertEqual(
            [self.get_datetime((2014, 4, 4, 21, 45))],
            self.callFUT(
                'weekly', start=self.get_datetime((2014, 4, 4)),
                end=self.get_datetime((2014, 4, 5))))


class NextDateOfSameWeekdayTests(unittest.TestCase,
                                 icemac.ab.calendar.testing.TestMixIn):
    """Testing ..recurrence.next_date_of_same_weekday()."""

    def callFUT(self, wd_src, base_date):
        from ..recurrence import next_date_of_same_weekday
        return next_date_of_same_weekday(wd_src, base_date)

    def test_weekday_of_wd_src_smaller_than_weekday_of_base_date(self):
        self.assertEqual(self.get_datetime((2014, 7, 28, 10)),
                         self.callFUT(self.get_datetime((2014, 7, 21, 10)),
                                      self.get_datetime((2014, 7, 23, 10))))

    def test_weekday_of_wd_src_greater_than_weekday_of_base_date(self):
        # Weekday of 2014-07-20 is 7 (Sunday)
        self.assertEqual(self.get_datetime((2014, 7, 27, 10)),
                         self.callFUT(self.get_datetime((2014, 7, 20, 10)),
                                      self.get_datetime((2014, 7, 23, 10))))

    def test_weekday_of_wd_src_equal_to_weekday_of_base_date(self):
        self.assertEqual(self.get_datetime((2014, 7, 17, 10)),
                         self.callFUT(self.get_datetime((2014, 7, 10, 10)),
                                      self.get_datetime((2014, 7, 17, 10))))

    def test_wd_src_equal_to_base_date(self):
        dt = self.get_datetime((2014, 7, 23, 17))
        self.assertEqual(dt, self.callFUT(dt, dt))
