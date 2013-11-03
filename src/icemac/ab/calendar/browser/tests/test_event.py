import icemac.ab.calendar.testing


def get_datetime_today_8_32_am():
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
        self.formatted_datetime = self.datetime.strftime('%y/%m/%d %H:%M')

    def test_navigation_to_calendar_is_possible(self):
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab')
        browser.getLink('Calendar').click()
        self.assertEqual('http://localhost/ab/++attribute++calendar',
                         browser.url)

    def test_event_can_be_added_and_is_shown_in_calendar(self):
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getLink('event').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/@@addEvent.html',
            browser.url)
        browser.getControl('datetime').value = self.formatted_datetime
        browser.getControl('event category').displayValue = ['wedding day']
        browser.getControl('Add', index=1).click()
        self.assertEqual('http://localhost/ab/++attribute++calendar',
                         browser.url)
        self.assertEqual(['"wedding day" added.'], browser.get_messages())
        # New event shows up in calendar:
        self.assertIn('08:32', browser.contents)

    def test_event_can_be_edited(self):
        event = self.create_event(datetime=self.datetime)
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab/++attribute++calendar')
        browser.getLink('Edit').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/Event', browser.url)
        self.assertEqual(
            self.formatted_datetime, browser.getControl('datetime').value)
        browser.getControl('event category').displayValue = ['wedding day']
        browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], browser.get_messages())
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar', browser.url)
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
        self.assertEqual('http://localhost/ab/++attribute++calendar',
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
