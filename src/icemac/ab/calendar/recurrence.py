from icemac.addressbook.i18n import _
from datetime import timedelta, datetime
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import zope.component
import zope.interface.common.idatetime


ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(days=7)


def get_recurrences(datetime, period, interval_start, interval_end):
    """Convenience function to get an interable of datetime objects of
    recurrences of `period` within the interval.

    period ... string, name of an adapter, see below
    interval_start ... date, part of the interval
    interval_end ... date, _not_ part of the interval

    """
    recurring = zope.component.getAdapter(
        datetime, icemac.ab.calendar.interfaces.IRecurringDateTime,
        name=period)
    return recurring(interval_start, interval_end)


class RecurringDateTime(grok.Adapter):
    """Base class for recurring datestimes."""

    grok.context(zope.interface.common.idatetime.IDateTime)
    grok.implements(icemac.ab.calendar.interfaces.IRecurringDateTime)
    grok.baseclass()

    def __call__(self, interval_start, interval_end):
        self.interval_start = interval_start
        self.interval_end = interval_end
        return self.compute()

    def compute(self):
        raise NotImplementedError('Implement in subclass!')


class Weekly(RecurringDateTime):
    """Recurring weekly on the same weekday."""

    grok.name('weekly')
    weight = 10
    title = _(u'weekly, same weekday')

    def compute(self):
        current_date = self.interval_start
        if current_date <= self.context:
            current_date = self.context
        else:
            weekday = self.context.isoweekday()
            while current_date.isoweekday() != weekday:
                current_date += ONE_DAY
        time = self.context.timetz()
        while current_date < self.interval_end:
            yield datetime.combine(current_date, time)
            current_date += ONE_WEEK
