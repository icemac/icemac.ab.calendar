# -*- coding: utf-8 -*-
import datetime
import icemac.addressbook.testing
import icemac.recurrence.conftest
import pytz


class Browser(icemac.addressbook.testing.Browser):
    """Browser adapted for calendar."""

    CALENDAR_OVERVIEW_URL = 'http://localhost/ab/++attribute++calendar'
    CALENDAR_MONTH_OVERVIEW_URL = (
        'http://localhost/ab/++attribute++calendar/@@month.html')
    CALENDAR_MONTH_LIST_VIEW_URL = (
        'http://localhost/ab/++attribute++calendar/@@month-list.html')
    CALENDAR_YEAR_OVERVIEW_URL = (
        'http://localhost/ab/++attribute++calendar/@@year.html')

    CALENDAR_MASTERDATA_URL = 'http://localhost/ab/@@calendar-masterdata.html'
    CALENDAR_MASTERDATA_EDIT_DISPLAY_URL = (
        'http://localhost/ab/++attribute++calendar/@@edit-display.html')

    CALENDAR_EVENT_FIELDS_LIST_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.ab.calendar.event.Event')

    CALENDAR_CATEGORIES_LIST_URL = (
        'http://localhost/ab/++attribute++calendar_categories')
    CALENDAR_CATEGORY_ADD_URL = (
        'http://localhost/ab/++attribute++calendar_categories/'
        '@@addEventCategory.html')
    CALENDAR_CATEGORY_EDIT_URL = (
        'http://localhost/ab/++attribute++calendar_categories/Category')
    CALENDAR_CATEGORY_DELETE_URL = (
        'http://localhost/ab/++attribute++calendar_categories/Category/'
        '@@delete.html')

    CALENDAR_RECURRING_EVENTS_LIST_URL = (
        'http://localhost/ab/++attribute++calendar_recurring_events')
    CALENDAR_RECURRING_EVENT_ADD_URL = (
        'http://localhost/ab/++attribute++calendar_recurring_events/'
        '@@addRecurringEvent.html')
    CALENDAR_RECURRING_EVENT_EDIT_URL = (
        'http://localhost/ab/++attribute++calendar_recurring_events/'
        'RecurringEvent')
    CALENDAR_RECURRING_EVENT_DELETE_URL = (
        'http://localhost/ab/++attribute++calendar_recurring_events/'
        'RecurringEvent/@@delete.html')

    EVENT_ADD_URL = 'http://localhost/ab/++attribute++calendar/@@addEvent.html'
    EVENT_EDIT_URL = 'http://localhost/ab/++attribute++calendar/Event'
    EVENT_CLONE_URL = (
        'http://localhost/ab/++attribute++calendar/Event/@@clone.html')
    EVENT_DELETE_URL = (
        'http://localhost/ab/++attribute++calendar/Event/@@delete.html')

    RECURRED_EVENT_CUSTOMIZE_URL = (
        'http://localhost/ab/++attribute++calendar/@@customize-recurred-event')
    RECURRED_EVENT_ADD_URL = (
        'http://localhost/ab/++attribute++calendar/@@addFromRecurredEvent.html'
    )
    RECURRED_EVENT_VIEW_URL = (
        'http://localhost/ab/++attribute++calendar/@@viewRecurredEvent.html')
    RECURRED_EVENT_DELETE_URL = ('http://localhost/ab/++attribute++calendar/'
                                 '@@delete-recurred-event.html')


class CalendarWebdriverPageObjectBase(
        icemac.addressbook.testing.WebdriverPageObjectBase):
    """Base for page object classes to used with to ``Webdriver.attach()``."""

    browser = Browser


class POCalendar(CalendarWebdriverPageObjectBase):
    """Webdriver page object for the calendar itself."""

    paths = [
        'CALENDAR_MONTH_OVERVIEW_URL',
        'CALENDAR_YEAR_OVERVIEW_URL',
    ]

    @property
    def month(self):
        return self._selenium.getSelectedLabel(
            'id=form-widgets-calendar_month')

    @month.setter
    def month(self, month):
        self._selenium.select(
            'id=form-widgets-calendar_month', 'label={}'.format(month))

    def switch_to_previous_month(self):
        self._selenium.click(u"link=◄")

    def switch_to_next_month(self):
        self._selenium.click(u"link=►")

    @property
    def year(self):
        return int(self._selenium.getSelectedLabel(
            'id=form-widgets-calendar_year'))

    @year.setter
    def year(self, year):
        self._selenium.select(
            'id=form-widgets-calendar_year', 'label={}'.format(year))


icemac.addressbook.testing.Webdriver.attach(POCalendar, 'calendar')


def get_recurred_event(recurring_event, DateTime):
    """Get one recurred event at today.

    DateTime ... the DateTime fixture instance.
    """
    return recurring_event.get_events(
        DateTime.today_8_32_am,
        DateTime.add(DateTime.today_8_32_am, days=1),
        pytz.utc).next()


# Fixture helpers


class DateTimeClass(icemac.recurrence.conftest.DateTimeClass,
                    icemac.addressbook.testing.DateTimeClass):
    """Helper class to create and format datetime objects."""

    @property
    def today_8_32_am(self):
        """Get a datetime object for today with fixed time."""
        return datetime.datetime.combine(
            datetime.date.today(), datetime.time(8, 32, tzinfo=pytz.utc))
