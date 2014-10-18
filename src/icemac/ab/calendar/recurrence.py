from datetime import timedelta, datetime
from icemac.addressbook.i18n import _
import gocept.month
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import math
import zope.component
import zope.interface.common.idatetime


ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(days=7)
TWO_WEEKS = timedelta(days=14)


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


def _get_isoweekday_difference(date1, date2):
    """Difference of isoweekdays between days."""
    days = 7 - (date1.isoweekday() - date2.isoweekday())
    if days >= 7:
        days -= 7
    return days


def next_date_of_same_weekday(wd_src, base_date, additional_weeks=0):
    """Compute next day with the same weekday as `wd_src` from `base_date` on.

    If `additional_weeks` is not zero, its number of weeks are added
    afterwards.
    If `wd_src` and `base_date` have the same weekday `base_date` is returned.

    """
    add_days = _get_isoweekday_difference(base_date, wd_src)
    return base_date + (add_days + additional_weeks * 7) * ONE_DAY


def recurrences_of_weekday_in_month(date, month):
    """Return number of recurrences of weekday of `date` in `month`."""
    minus_days = _get_isoweekday_difference(month.firstOfMonth(), date)
    return int(math.ceil((month.lastOfMonth().day - minus_days) / 7.0))


def add_years(date, years):
    """Add `years` number of years to date."""
    try:
        return date.replace(year=date.year + years)
    except ValueError:
        # Handle 29th of february as 28th in non-leap years:
        return date.replace(year=date.year + years, day=date.day - 1)


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


class SameWeekdayBase(RecurringDateTime):
    """Base class for recurrences on the same weekday."""

    grok.baseclass()
    interval = NotImplemented

    def compute(self):
        current_date = self.interval_start
        if current_date <= self.context:
            current_date = self.context
        else:
            current_date = next_date_of_same_weekday(
                self.context, current_date)
        time = self.context.timetz()
        while current_date < self.interval_end:
            yield datetime.combine(current_date, time)
            current_date += self.interval


class Weekly(SameWeekdayBase):
    """Recurring weekly on the same weekday."""

    grok.name('weekly')
    weight = 10
    title = _('weekly, same weekday (e. g. each Friday)')
    interval = ONE_WEEK


class BiWeekly(SameWeekdayBase):
    """Recurring biweekly on the same weekday."""

    grok.name('biweekly')
    weight = 11
    title = _('every other week, same weekday (e. g. each second Friday)')
    interval = TWO_WEEKS


class SameNthWeekdayInMonthBase(RecurringDateTime):
    """Base class for recurrings on the same day nth weekday in month."""

    grok.baseclass()
    month_interval = NotImplemented

    def compute(self):
        if self.context > self.interval_end:
            return  # no need to compute: there will be no results
        n = int(math.ceil(self.context.day / 7.0)) - 1
        month = gocept.month.IMonth(self.interval_start.date())
        time = self.context.timetz()
        while True:
            result = next_date_of_same_weekday(
                self.context, datetime.combine(month.firstOfMonth(), time), n)
            try:
                if result.month != month.month:
                    continue  # result has swapped into next month
            finally:
                month += self.month_interval
            if result >= self.interval_end:
                break
            if result < self.context:
                continue
            yield result


class MonthlyNthWeekday(SameNthWeekdayInMonthBase):
    """Recurring monthly on same recurrence of the weekday in the month as in
       `self.context`.

    """
    grok.name('nth weekday of month')
    weight = 20
    title = _('monthly, same weekday (e. g. each 3rd Sunday)')
    month_interval = 1


class BiMonthlyNthWeekday(SameNthWeekdayInMonthBase):
    """Recurring monthly on same recurrence of the weekday in the month as in
       `self.context` but only every other month.

    """
    grok.name('nth weekday every other month')
    weight = 21
    title = _('every other month, same weekday '
              '(e. g. each 3rd Sunday in other month)')
    month_interval = 2


class Yearly(RecurringDateTime):
    """Recurring on the same date each year."""

    grok.name('yearly')
    weight = 100
    title = _('yearly (e. g. 24th of December)')

    def compute(self):
        if self.context > self.interval_end:
            return  # no need to compute: there will be no results
        date = self.context
        index = 0
        while date < self.interval_start:
            index += 1
            date = add_years(self.context, index)
        while date < self.interval_end:
            yield date
            index += 1
            date = add_years(self.context, index)
