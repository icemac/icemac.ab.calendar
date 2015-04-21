from mock import Mock
import datetime
import icemac.ab.calendar.testing


class IDatetimeTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..interfaces.IDatetime"""

    def validate(self, obj):
        import zope.schema
        from ..interfaces import IDatetime
        return zope.schema.getValidationErrors(IDatetime, obj)

    def create_datetime(self, date, time, whole_day_event):
        mock = Mock()
        if date:
            mock.date = datetime.date(2015, 4, 15)
        else:
            mock.date = None
        if time:
            mock.time = datetime.time(18, 29)
        else:
            mock.time = None
        mock.whole_day_event = bool(whole_day_event)
        return mock

    def test_whole_day_event_with_time_is_valid(self):
        dt = self.create_datetime('date', 'time', 'whole_day')
        self.assertEqual([], self.validate(dt))

    def test_whole_day_event_without_time_is_valid(self):
        dt = self.create_datetime('date', None, 'whole_day')
        self.assertEqual([], self.validate(dt))

    def test_non_whole_day_event_with_time_is_valid(self):
        dt = self.create_datetime('date', 'time', whole_day_event=False)
        self.assertEqual([], self.validate(dt))

    def test_non_whole_day_event_without_time_is_invalid(self):
        dt = self.create_datetime('date', None, whole_day_event=False)
        v = self.validate(dt)
        self.assertEqual(1, len(v))
        self.assertEqual('Either enter a `time` or select `whole day event`!',
                         str(v[0][1]))
