# -*- coding: utf-8 -*-
from icemac.ab.calendar.interfaces import ICalendarDisplaySettings
from icemac.ab.calendar.interfaces import IEvent, IRecurringEvent
from icemac.ab.calendar.testing import CalendarWebdriverPageObjectBase
from icemac.ab.calendar.testing import get_recurred_event
from icemac.addressbook.testing import Webdriver
from zope.testbrowser.browser import HTTPError
from zope.traversing.browser import absoluteURL
import calendar
import pytest
import pytz
import zope.component.hooks


def test_event__Add__1(address_book, CategoryFactory, DateTime, browser):
    """It can add events which shown up in the calendar."""
    CategoryFactory(address_book, u'wedding day')
    dt = DateTime.today_8_32_am
    formatted_time = dt.strftime('%H:%M')
    formatted_date = DateTime.format_date(dt)
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    browser.getLink('event').click()
    assert browser.EVENT_ADD_URL == browser.url
    browser.getControl('date').value = formatted_date
    browser.getControl('time').value = formatted_time
    browser.getControl('event category').displayValue = ['wedding day']
    browser.getControl('Add', index=1).click()
    assert '"wedding day" added.' == browser.message
    assert browser.CALENDAR_MONTH_OVERVIEW_URL == browser.url
    # The new event shows up in the calendar:
    assert formatted_time in browser.contents


def test_event__Add__2(address_book, browser):
    """It is not accessible for a calendar visitor."""
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.EVENT_ADD_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def test_event__Edit__1(
        address_book, EventFactory, CategoryFactory, DateTime, browser):
    """It allows to edit an event."""
    CategoryFactory(address_book, u'wedding day')
    dt = DateTime.today_8_32_am
    EventFactory(address_book, datetime=dt)
    browser.login('cal-editor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    browser.getLink('event', index=1).click()
    assert browser.EVENT_EDIT_URL == browser.url
    assert DateTime.format_date(dt) == browser.getControl('date').value
    assert dt.strftime('%H:%M') == browser.getControl('time').value
    browser.getControl('event category').displayValue = ['wedding day']
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.CALENDAR_MONTH_OVERVIEW_URL == browser.url
    browser.getLink('wedding day').click()
    assert ['wedding day'] == browser.getControl('event category').displayValue


def test_event__Edit__2(address_book, EventFactory, DateTime, browser):
    """It is not accessible for a calendar visitor."""
    EventFactory(address_book, datetime=DateTime.today_8_32_am)
    browser.login('cal-visitor')
    browser.open(browser.EVENT_EDIT_URL)
    # There are no fields to edit and no delete or clone button:
    assert (['form.buttons.apply', 'form.buttons.cancel'] ==
            browser.all_control_names)


def test_event__Edit__3(
        address_book, UserFactory, EventFactory, DateTime, browser):
    """It can be accessed by a local calendar user."""
    UserFactory(address_book, u'Hans', u'Tester', u'hans@example.com',
                '1qay2wsx', ['Calendar editor'])
    EventFactory(address_book, datetime=DateTime.today_8_32_am)
    browser.formlogin('hans@example.com', '1qay2wsx')
    browser.open(browser.EVENT_EDIT_URL)
    assert len(browser.all_control_names) > 2


def test_event__Edit__4(
        address_book, EventFactory, PersonFactory, KeywordFactory,
        CategoryFactory, DateTime, browser):
    """It does not break if list of persons gets restricted by keyword.

    If a person is selected which does not have the person restriction
    keyword (see ICalendarDisplaySettings.person_keyword) the view does not
    break but renders the person as "missing".

    It renders an error message with the missing person selected.
    After deselecting the person the event can be saved again.
    """
    EventFactory(address_book,
                 datetime=DateTime.today_8_32_am,
                 category=CategoryFactory(address_book, u'foo'),
                 persons=set([PersonFactory(address_book, u'Tester')]))
    browser.login('cal-editor')
    browser.handleErrors = False
    browser.open(browser.EVENT_EDIT_URL)
    assert ['Tester'] == browser.getControl('persons').displayValue
    browser.getControl('notes').value = 'Force save'
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    kw = KeywordFactory(address_book, u'foo')
    with zope.component.hooks.site(address_book):
        ICalendarDisplaySettings(address_book.calendar).person_keyword = kw
    browser.open(browser.EVENT_EDIT_URL)
    assert ['Missing: Tester'] == browser.getControl('persons').displayValue
    browser.getControl('notes').value = 'Force save, second time'
    browser.handleErrors = False
    browser.getControl('Apply').click()
    assert 'There were some errors.' in browser.contents
    assert ('Please deselect the persons prefixed with "Missing:"' in
            browser.contents)
    browser.getControl('persons').displayValue = []
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message


def test_event__Delete__1(address_book, EventFactory, DateTime, browser):
    """It allows to delete an event after a confirmation."""
    EventFactory(address_book, datetime=DateTime.today_8_32_am)
    browser.login('cal-editor')
    browser.open(browser.EVENT_EDIT_URL)
    browser.getControl('Delete').click()
    assert 'Do you really want to delete this event?' in browser.contents
    assert browser.EVENT_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert '"event" deleted.' == browser.message
    assert browser.CALENDAR_MONTH_OVERVIEW_URL == browser.url


def test_event__Delete__2(
        address_book, EventFactory, CategoryFactory, DateTime, browser):
    """It renders a nice message if the event only has a category."""
    EventFactory(address_book, datetime=DateTime.today_8_32_am,
                 category=CategoryFactory(address_book, u'foo'))
    browser.login('cal-editor')
    browser.open(browser.EVENT_DELETE_URL)
    browser.getControl('Yes').click()
    assert '"foo" deleted.' == browser.message


def test_event__Delete__3(address_book, EventFactory, DateTime, browser):
    """It is not accessible for a calendar visitor."""
    EventFactory(address_book, datetime=DateTime.today_8_32_am)
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.EVENT_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def test_event__Clone__1(address_book, EventFactory, DateTime, browser):
    """It clones an event after a confirmation."""
    EventFactory(address_book, datetime=DateTime.today_8_32_am)
    browser.login('cal-editor')
    browser.open(browser.EVENT_EDIT_URL)
    browser.getControl('Clone event').click()
    assert browser.EVENT_CLONE_URL == browser.url
    assert (['form.buttons.action', 'form.buttons.cancel'] ==
            browser.submit_control_names)
    browser.getControl('Yes').click()
    assert '"event" cloned.' == browser.message
    # Clone leads to edit view of cloned event:
    assert '{0.EVENT_EDIT_URL}-2'.format(browser) == browser.url


def test_event__Clone__2(address_book, EventFactory, DateTime, browser):
    """It is not accessible for a calendar visitor."""
    EventFactory(address_book, datetime=DateTime.today_8_32_am)
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.EVENT_CLONE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


@pytest.fixture('function')
def sample_recurring_event(
        address_book, FieldFactory, CategoryFactory, RecurringEventFactory,
        PersonFactory, DateTime):
    """Example of a recurring event."""
    CategoryFactory(address_book, u'aaz')
    bar = CategoryFactory(address_book, u'bar')
    PersonFactory(address_book, u'Bester')
    tester = PersonFactory(address_book, u'Tester')
    FieldFactory(address_book, IEvent, u'Text', u'foobar')
    foobar = FieldFactory(
        address_book, IRecurringEvent, u'Text', u'foobar').__name__
    return RecurringEventFactory(
        address_book,
        **{'category': bar,
           foobar: u'qux',
           'datetime': DateTime(2014, 5, 24, 10, 30),
           'alternative_title': u'foo bär',
           'period': u'daily',
           'persons': set([tester]),
           'external_persons': [u'Mr. Developer'],
           'text': u'Important'})


def get_recurred_event_url(recurred_event, request):
    """Get the URL of a recurred event."""
    return absoluteURL(recurred_event, request).replace(
        'http://127.0.0.1/', 'http://localhost/')


@pytest.fixture('function')
def sample_recurred_event_url(
        sample_recurring_event, RequestFactory, DateTime):
    """Sample of a recurred event.

    Returns the URL to the @@customize-recurred-event view.
    """
    return get_recurred_event_url(
        get_recurred_event(sample_recurring_event, DateTime), RequestFactory())


def test_event__ViewRecurredEvent__1(
        address_book, sample_recurred_event_url, browser):
    """It renders a display form for a calendar visitor."""
    browser.login('cal-visitor')
    browser.open(sample_recurred_event_url)
    assert browser.RECURRED_EVENT_VIEW_URL == browser.url
    assert (['form.buttons.apply', 'form.buttons.cancel'] ==
            browser.all_control_names)


def test_event__AddFromRecurredEvent__1(
        address_book, DateTime, sample_recurred_event_url, browser):
    """It prefills the form from the recurring event."""
    browser.login('cal-editor')
    browser.open(sample_recurred_event_url)
    assert browser.RECURRED_EVENT_ADD_URL == browser.url
    assert ['bar'] == browser.getControl('event category').displayValue
    assert (DateTime.format_date(DateTime.now) ==
            browser.getControl('date').value)
    assert '10:30' == browser.getControl('time').value
    assert ('foo bär' ==
            browser.getControl('alternative title to category').value)
    assert ['Tester'] == browser.getControl('persons').displayValue
    assert ('Mr. Developer' ==
            browser.getControl(name='form.widgets.external_persons.0').value)
    assert 'Important' == browser.getControl('notes').value
    assert 'qux' == browser.getControl('foobar').value


def test_event__AddFromRecurredEvent__2(
        address_book, sample_recurred_event_url, browser):
    """It saves changes made in the form."""
    browser.login('cal-editor')
    browser.open(sample_recurred_event_url)
    browser.getControl('alternative title to category').value = 'birthday'
    browser.getControl('Apply').click()
    assert '"birthday" added.' == browser.message
    browser.open(browser.EVENT_EDIT_URL)
    assert 'birthday' == browser.getControl('alternative').value


def test_event__AddFromRecurredEvent__2_5(
        address_book, CategoryFactory, RecurringEventFactory, DateTime,
        RequestFactory, TimeZonePrefFactory, browser):
    """It keeps the time value in DST."""
    recurring_event = RecurringEventFactory(
        address_book,
        category=CategoryFactory(address_book, u'bar'),
        datetime=DateTime(2016, 3, 24, 12),
        period=u'weekly')
    recurred_event = recurring_event.get_events(
        DateTime(2016, 3, 27, 0), DateTime(2016, 4, 1, 0), pytz.utc).next()
    url = get_recurred_event_url(recurred_event, RequestFactory())
    TimeZonePrefFactory('Europe/Berlin')
    browser.login('cal-editor')
    browser.open(url)
    # Without making sure the local time stays the same also in DST the time
    # would be 14:00 because in DST Berlin is 2 hours ahead of UTC.
    assert '13:00' == browser.getControl('time').value


def test_event__AddFromRecurredEvent__3(
        address_book, sample_recurred_event_url, browser):
    """It does not change anything if `cancel` gets hit."""
    browser.login('cal-editor')
    browser.open(sample_recurred_event_url)
    browser.getControl('Cancel').click()
    assert 'Addition canceled.' == browser.message
    assert 0 == len(address_book.calendar)


def test_event__AddFromRecurredEvent__4(address_book, browser):
    """It is not accessible for a calendar visitor."""
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.RECURRED_EVENT_ADD_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def days_in_month(date):
    """Number of days in the month `date` belongs to."""
    return calendar.monthrange(date.year, date.month)[1]


def test_event__DeleteRecurredEvent__1(
        address_book, sample_recurred_event_url, DateTime, browser):
    """It deletes the recurred event after a confirmation."""
    browser.login('cal-editor')
    browser.open(sample_recurred_event_url)
    browser.getControl('Delete').click()
    assert browser.RECURRED_EVENT_DELETE_URL == browser.url
    assert ('Do you really want to delete this recurred event?' in
            browser.contents)
    browser.getControl('Yes').click()
    assert u'"foo bär" deleted.' == browser.message
    days = days_in_month(DateTime.now)  # -1 deleted event +1 browser.message
    assert days == browser.contents.count('foo bär')
    assert address_book.calendar['Event'].deleted


def test_event__DeleteRecurredEvent__1_5(
        address_book, sample_recurring_event, sample_recurred_event_url,
        DateTime, browser):
    """It deletes a whole day recurred event, too."""
    sample_recurring_event.whole_day_event = True
    browser.login('cal-editor')
    browser.open(sample_recurred_event_url)
    browser.getControl('Delete').click()
    browser.getControl('Yes').click()
    assert u'"foo bär" deleted.' == browser.message
    days = days_in_month(DateTime.now)  # -1 deleted event +1 browser.message
    assert days == browser.contents.count('foo bär')


def test_event__DeleteRecurredEvent__2(
        address_book, sample_recurring_event, RequestFactory, DateTime,
        browser):
    """It renders a nice message if the recurring event has only a category."""
    sample_recurring_event.alternative_title = None
    browser.login('cal-editor')
    browser.open(get_recurred_event_url(
        get_recurred_event(sample_recurring_event, DateTime),
        RequestFactory()))
    browser.getControl('Delete').click()
    browser.getControl('Yes').click()
    assert u'"bar" deleted.' == browser.message


def test_event__DeleteRecurredEvent__3(address_book, browser):
    """It is not accessible for a calendar visitor."""
    browser.login('cal-visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.RECURRED_EVENT_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


@pytest.fixture('function')
def sample_event_webdriver(address_book, EventFactory, DateTime):
    """Create a sample event."""
    return EventFactory(address_book, datetime=DateTime.today_8_32_am)


class POEvent(CalendarWebdriverPageObjectBase):
    """Webdriver page object for an event object itself."""

    paths = [
        'EVENT_EDIT_URL',
    ]

    # property setter!
    def set_whole_day_event(self, value):
        self._selenium.click(
            'id=form-widgets-datetime-widgets-whole_day_event-{}'.format(
                int(not(value))))

    whole_day_event = property(None, set_whole_day_event)

    status_attr_map = {
        'hidden': 'assertNotVisible',
        'shown': 'assertVisible',
        'wait-for-hidden': 'waitForNotVisible',
        'wait-for-shown': 'waitForVisible',
    }

    def assert_time(self, status):
        """Assert display status of time widget.

        Possible status see keys of `status_attr_map`.
        """
        getattr(self._selenium, self.status_attr_map[status])(
            'id=form-widgets-datetime-widgets-time')


Webdriver.attach(POEvent, 'event')


@pytest.mark.webdriver
def test_event__WidgetToggle__1_webdriver(sample_event_webdriver, webdriver):
    """The time widget is initially hidden for whole day events."""
    sample_event_webdriver.whole_day_event = True
    webdriver.login('cal-editor', webdriver.event.EVENT_EDIT_URL)
    webdriver.event.assert_time('hidden')


@pytest.mark.webdriver
def test_event__WidgetToggle__2_webdriver(sample_event_webdriver, webdriver):
    """The time widget is initially shown for non whole day events."""
    sample_event_webdriver.whole_day_event = False
    webdriver.login('cal-editor', webdriver.event.EVENT_EDIT_URL)
    webdriver.event.assert_time('shown')


@pytest.mark.webdriver
def test_event__WidgetToggle__3_webdriver(sample_event_webdriver, webdriver):
    """Changing an event to a whole day event hides the time widget."""
    sample_event_webdriver.whole_day_event = False
    webdriver.login('cal-editor', webdriver.event.EVENT_EDIT_URL)
    webdriver.event.whole_day_event = True
    webdriver.event.assert_time('wait-for-hidden')


@pytest.mark.webdriver
def test_event__WidgetToggle__4_webdriver(sample_event_webdriver, webdriver):
    """Changing an event to a non-whole day event shows the time widget."""
    sample_event_webdriver.whole_day_event = True
    webdriver.login('cal-editor', webdriver.event.EVENT_EDIT_URL)
    webdriver.event.whole_day_event = False
    webdriver.event.assert_time('wait-for-shown')


@pytest.mark.webdriver
def test_event__WidgetToggle__5_webdriver(sample_event_webdriver, webdriver):
    """Clicking on a selected event kind does not toggle the time display."""
    sample_event_webdriver.whole_day_event = True
    webdriver.login('cal-editor', webdriver.event.EVENT_EDIT_URL)
    webdriver.event.assert_time('hidden')
    webdriver.event.whole_day_event = True
    webdriver.event.assert_time('wait-for-hidden')
