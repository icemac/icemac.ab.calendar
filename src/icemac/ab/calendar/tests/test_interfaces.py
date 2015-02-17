from datetime import date
import icemac.ab.calendar.testing


class IBaseEventTests(icemac.ab.calendar.testing.ZODBTestCase):
    """Testing ..interfaces.IBaseEvent"""

    def validate(self, obj):
        import zope.schema
        from ..interfaces import IBaseEvent
        return zope.schema.getValidationErrors(IBaseEvent, obj)

    def create_event(self, **kw):
        kw['category'] = self.create_category(u'foo')
        return super(IBaseEventTests, self).create_event(**kw)

    def test_whole_day_event_with_date_without_time_is_valid(self):
        event = self.create_event(
            whole_day_event=True, date_without_time=date(1977, 11, 24))
        self.assertEqual([], self.validate(event))

    def test_whole_day_event_without_date_without_time_is_invalid(self):
        event = self.create_event(whole_day_event=True, date_without_time=None)
        v = self.validate(event)
        self.assertEqual(1, len(v))
        self.assertEqual('Date must be entered.', str(v[0][1]))

    def test_non_whole_day_event_with_datetime_is_valid(self):
        event = self.create_event(
            whole_day_event=False, datetime=self.get_datetime())
        self.assertEqual([], self.validate(event))

    def test_non_whole_day_event_without_datetime_is_invalid(self):
        event = self.create_event(whole_day_event=False, datetime=None)
        v = self.validate(event)
        self.assertEqual(1, len(v))
        self.assertEqual('Date must be entered.', str(v[0][1]))
