import icemac.ab.calendar.testing


class RecurrenceTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Testing ..recurrence.*"""

    def setUp(self):
        super(RecurrenceTests, self).setUp()
        self.recurrence_start = self.get_datetime((2013, 5, 3, 21, 45))
        self.interval_start = self.get_datetime((2014, 4, 1))
        self.interval_end = self.get_datetime((2014, 4, 30))

    def callFUT(self, adapter_name, datetime=None, start=None, end=None):
        from icemac.ab.calendar.recurrence import get_recurrences
        datetime = self.recurrence_start if datetime is None else datetime
        start = self.interval_start if start is None else start
        end = self.interval_end if end is None else end
        return list(get_recurrences(datetime, adapter_name, start, end))

    def test_Weekly_fulfills_IRecurringDateTime_interface(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import IRecurringDateTime
        from ..recurrence import Weekly
        self.assertTrue(verifyObject(IRecurringDateTime, Weekly(None)))

    def test_weekly_returns_all_dates_in_interval_for_same_weekday(self):
        self.assertEqual(
            [self.get_datetime((2014, 4, 4, 21, 45)),
             self.get_datetime((2014, 4, 11, 21, 45)),
             self.get_datetime((2014, 4, 18, 21, 45)),
             self.get_datetime((2014, 4, 25, 21, 45))], self.callFUT('weekly'))
        self.assertEqual(self.recurrence_start.isoweekday(),
                         self.callFUT('weekly')[0].isoweekday())

    def test_weekly_does_not_start_before_datetime(self):
        self.assertEqual(
            [self.get_datetime((2014, 4, 18, 21, 45)),
             self.get_datetime((2014, 4, 25, 21, 45))],
            self.callFUT('weekly',
                         datetime=self.get_datetime((2014, 4, 18, 21, 45))))
        self.assertEqual(self.recurrence_start.isoweekday(),
                         self.callFUT('weekly')[0].isoweekday())

    def test_weekly_returns_empty_interval_if_datetime_after_interval_end(
            self):
        self.assertEqual(
            [],
            self.callFUT('weekly',
                         datetime=self.get_datetime((2014, 5, 1, 21, 45))))

    def test_weekly_interval_end_does_not_belong_to_interval(self):
        self.assertEqual(
            [],
            self.callFUT(
                'weekly', start=self.get_datetime((2014, 4, 24)),
                end=self.get_datetime((2014, 4, 25))))

    def test_weekly_interval_start_belongs_to_interval(self):
        self.assertEqual(
            [self.get_datetime((2014, 4, 4, 21, 45))],
            self.callFUT(
                'weekly', start=self.get_datetime((2014, 4, 4)),
                end=self.get_datetime((2014, 4, 5))))
