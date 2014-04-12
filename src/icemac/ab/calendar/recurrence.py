from icemac.addressbook.i18n import _
from datetime import timedelta
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import zope.component
import zope.interface.common.idatetime


ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(days=7)


def get_recurrings(date, period, interval_start, interval_end):
    """Convenience function to get an interable of date objects of recurrences
    of `period` within the interval.

    period ... string, name of an adapter, see below
    interval_start ... date, part of the interval
    interval_end ... date, _not_ part of the interval

    """
    recurring = zope.component.getAdapter(
        date, icemac.ab.calendar.interfaces.IRecurringDate, name=period)
    return recurring(interval_start, interval_end)


class RecurringDate(grok.Adapter):
    """Base class for recurring dates."""

    grok.context(zope.interface.common.idatetime.IDate)
    grok.implements(icemac.ab.calendar.interfaces.IRecurringDate)
    grok.baseclass()

    def __call__(self, interval_start, interval_end):
        self.interval_start = interval_start
        self.interval_end = interval_end
        return self.compute()

    def compute(self):
        raise NotImplementedError('Implement in subclass!')


class Weekly(RecurringDate):
    """Recurring weekly on the same weekday."""

    grok.name('weekly')
    weight = 10
    title = _(u'weekly, same weekday')

    def compute(self):
        weekday = self.context.isoweekday()
        current_date = self.interval_start
        while current_date.isoweekday() != weekday:
            current_date += ONE_DAY
        while current_date < self.interval_end:
            yield current_date
            current_date += ONE_WEEK
