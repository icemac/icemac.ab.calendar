# -*- coding: utf-8 -*-
import icemac.ab.calendar.testing


def get_datetime_today_8_32_am():
    """Get a datetime object for today with fixed time."""
    from datetime import date, time, datetime
    from pytz import utc
    return datetime.combine(date.today(), time(8, 32, tzinfo=utc))


class EventCRUD(icemac.ab.calendar.testing.BrowserTestCase):

    """CRUD testing for ..event.*"""

    def setUp(self):
        super(EventCRUD, self).setUp()
        self.create_category(u'birthday')
        self.create_category(u'wedding day')
        self.datetime = get_datetime_today_8_32_am()
        self.formatted_datetime = self.format_datetime(self.datetime)
        self.formatted_date = self.format_date(self.datetime)
        self.formatted_time = self.datetime.strftime('%H:%M')

    def test_navigation_to_calendar_is_possible(self):
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab')
        browser.getLink('Calendar').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/@@month.html',
            browser.url)

    def test_event_can_be_added_and_is_shown_in_calendar(self):
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getLink('event').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/@@addEvent.html',
            browser.url)
        browser.getControl('date').value = self.formatted_date
        browser.getControl('time').value = self.formatted_time
        browser.getControl('event category').displayValue = ['wedding day']
        browser.getControl('Add', index=1).click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/@@month.html',
            browser.url)
        self.assertEqual(['"wedding day" added.'], browser.get_messages())
        # New event shows up in calendar:
        self.assertIn(self.formatted_time, browser.contents)

    def test_event_can_be_edited(self):
        self.create_event(datetime=self.datetime)
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getLink('Edit').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/Event', browser.url)
        self.assertEqual(self.formatted_date, browser.getControl('date').value)
        self.assertEqual(self.formatted_time, browser.getControl('time').value)
        browser.getControl('event category').displayValue = ['wedding day']
        browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], browser.get_messages())
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/@@month.html',
            browser.url)
        browser.getLink('wedding day').click()
        self.assertEqual(['wedding day'],
                         browser.getControl('event category').displayValue)

    def test_event_can_be_deleted_after_confirmation(self):
        event = self.create_event(datetime=self.datetime)
        browser = self.get_browser('cal-editor')
        browser.open(
            'http://localhost/ab/++attribute++calendar/%s' % event.__name__)
        browser.getControl('Delete').click()
        self.assertIn('Do you really want to delete this event?',
                      browser.contents)
        browser.getControl('Yes').click()
        self.assertEqual(['"event" deleted.'], browser.get_messages())
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/@@month.html',
            browser.url)

    def test_event_can_be_cloned_after_confirmation(self):
        event = self.create_event(datetime=self.datetime)
        browser = self.get_browser('cal-editor')
        browser.open(
            'http://localhost/ab/++attribute++calendar/%s' % event.__name__)
        browser.getControl('Clone event').click()
        self.assertEqual(['form.buttons.action', 'form.buttons.cancel'],
                         browser.get_submit_control_names())
        browser.getControl('Yes').click()
        self.assertEqual(['"event" cloned.'], browser.get_messages())
        # Clone leads to edit view of cloned event:
        self.assertEqual('http://localhost/ab/++attribute++calendar/Event-2',
                         browser.url)


def get_customize_recurred_event_url(recurring_event):
    """Get the URL to customize a recurred event."""
    return ('http://localhost/ab/++attribute++calendar/'
            '@@customize-recurred-event?event=%s&date=%s' % (
                recurring_event.__name__,
                get_datetime_today_8_32_am().date().isoformat()))

ADD_FROM_RECURRED_EVENT_URL = (
    'http://localhost/ab/++attribute++calendar/@@addFromRecurredEvent.html')


class EventSecurity(icemac.ab.calendar.testing.BrowserTestCase):

    """Security tests for categories."""

    def test_visitor_is_not_able_to_add_events_even_if_he_knows_the_url(self):
        from mechanize import HTTPError
        browser = self.get_browser('cal-visitor')
        with self.assertRaises(HTTPError) as err:
            browser.open(
                'http://localhost/ab/++attribute++calendar/@@addEvent.html')
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))

    def test_visitor_is_able_to_view_edit_form_but_not_to_change(self):
        event = self.create_event(datetime=get_datetime_today_8_32_am())
        browser = self.get_browser('cal-visitor')
        browser.open(
            'http://localhost/ab/++attribute++calendar/%s' % event.__name__)
        # There are no fields to edit and no delete button:
        self.assertEqual(['form.buttons.apply', 'form.buttons.cancel'],
                         browser.get_all_control_names())

    def test_visitor_not_able_to_customize_recurred_event_even_knowing_the_url(
            self):
        from mechanize import HTTPError
        browser = self.get_browser('cal-visitor')
        with self.assertRaises(HTTPError) as err:
            browser.open(ADD_FROM_RECURRED_EVENT_URL)
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))

    def test_visitor_sees_display_form_when_looking_at_recurrend_event_details(
            self):
        recurring_event = self.create_recurring_event(
            datetime=get_datetime_today_8_32_am(),
            alternative_title=u'recurred event')
        browser = self.get_browser('cal-visitor')
        browser.handleErrors = False
        browser.open(get_customize_recurred_event_url(recurring_event))
        self.assertEqual(['form.buttons.apply', 'form.buttons.cancel'],
                         browser.get_all_control_names())


class AddFromRecurredEventTests(icemac.ab.calendar.testing.BrowserTestCase):

    """Testing ..event.AddFromRecurredEvent."""

    def setUp(self):
        from icemac.addressbook.testing import create_field, create
        from icemac.ab.calendar.interfaces import IEvent, IRecurringEvent
        super(AddFromRecurredEventTests, self).setUp()
        self.create_category(u'aaz')
        bar = self.create_category(u'bar')
        self.create_person(u'Bester')
        tester = self.create_person(u'Tester')
        ab = self.layer['addressbook']
        create_field(ab, IEvent, u'Text', u'foobar')
        foobar = create_field(ab, IRecurringEvent, u'Text', u'foobar')
        recurring_event = create(
            ab, ab.calendar_recurring_events,
            'icemac.ab.calendar.event.RecurringEvent', return_obj=True,
            **{'category': bar, foobar: u'qux',
               'datetime': self.get_datetime((2014, 5, 24, 10, 30)),
               'alternative_title': u'foo bär', 'period': u'weekly',
               'persons': set([tester]),
               'external_persons': [u'Mr. Developer'], 'text': u'Important'})
        self.browser = self.get_browser('cal-editor')
        self.browser.open(get_customize_recurred_event_url(recurring_event))

    def test_prefills_form_from_recurring_event(self):
        browser = self.browser
        self.assertEqual(ADD_FROM_RECURRED_EVENT_URL, browser.url)
        self.assertEqual(['bar'],
                         browser.getControl('event category').displayValue)
        self.assertEqual(self.format_date(self.get_datetime()),
                         browser.getControl('date').value)
        self.assertEqual('10:30', browser.getControl('time').value)
        self.assertEqual(
            'foo bär',
            browser.getControl('alternative title to category').value)
        self.assertEqual(['Tester'],
                         browser.getControl('persons').displayValue)
        self.assertEqual(
            'Mr. Developer',
            browser.getControl(name='form.widgets.external_persons.0').value)
        self.assertEqual('Important', browser.getControl('notes').value)
        self.assertEqual('qux', browser.getControl('foobar').value)

    def test_saves_changes_made_in_form(self):
        browser = self.browser
        browser.getControl('alternative title to category').value = 'birthday'
        browser.getControl('Apply').click()
        self.assertEqual(['"birthday" added.'], browser.get_messages())
        browser.getLink('birthday').click()
        self.assertEqual('birthday', browser.getControl('alternative').value)

    def test_cancel_does_not_change_anything(self):
        browser = self.browser
        browser.getControl('Cancel').click()
        self.assertEqual(['Addition canceled.'], browser.get_messages())
        self.assertEqual(0, len(self.layer['addressbook'].calendar))

    def test_delete_removes_recurred_event_after_confirmation(self):
        browser = self.browser
        browser.getControl('Delete').click()
        self.assertIn('Do you really want to delete this recurred event?',
                      browser.contents)
        browser.getControl('Yes').click()
        self.assertEqual([u'"foo bär" deleted.'], browser.get_messages())
        self.assertTrue(self.layer['addressbook'].calendar['Event'].deleted)


class EventSTests(icemac.ab.calendar.testing.SeleniumTestCase):

    """Selenium testing ../resources/calendar.js"""

    def create_event(self, whole_day_event):
        """Create an event, today at 08:32."""
        return super(EventSTests, self).create_event(
            datetime=get_datetime_today_8_32_am(),
            whole_day_event=whole_day_event)

    def login(self):
        super(EventSTests, self).login('cal-editor', 'cal-editor')
        sel = self.selenium
        sel.open('/ab/++attribute++calendar/Event')
        return sel

    def assert_time(self, status):
        """Assert display status of time widget: 'shown' or 'hidden'."""
        if status == 'hidden':
            self.selenium.waitForNotVisible(
                'id=form-widgets-datetime-widgets-time')
        else:
            self.selenium.waitForVisible(
                'id=form-widgets-datetime-widgets-time')

    def test_time_is_initially_hidden_for_whole_day_events(self):
        self.create_event(whole_day_event=True)
        self.login()
        self.assert_time('hidden')

    def test_time_is_initially_shown_for_non_whole_day_events(self):
        self.create_event(whole_day_event=False)
        self.login()
        self.assert_time('shown')

    def test_changing_event_to_whole_day_event_hides_time(self):
        self.create_event(whole_day_event=False)
        sel = self.login()
        sel.click('id=form-widgets-datetime-widgets-whole_day_event-0')
        self.assert_time('hidden')

    def test_changing_event_to_non_whole_day_event_shows_time(self):
        self.create_event(whole_day_event=True)
        sel = self.login()
        sel.click('id=form-widgets-datetime-widgets-whole_day_event-1')
        self.assert_time('shown')

    def test_clicking_on_selected_event_kind_does_not_toggle_time_display(
            self):
        self.create_event(whole_day_event=True)
        sel = self.login()
        self.assert_time('hidden')
        sel.click('id=form-widgets-datetime-widgets-whole_day_event-0')
        self.assert_time('hidden')
