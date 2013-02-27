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
        browser.getControl('date and time').value = self.formatted_datetime
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
            self.formatted_datetime, browser.getControl('date and time').value)
        browser.getControl('event category').displayValue = ['wedding day']
        browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], browser.get_messages())
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar', browser.url)
        browser.getLink('Edit').click()
        self.assertEqual(['wedding day'],
                         browser.getControl('event category').displayValue)

    def test_event_can_be_deleted(self):
        self.fail('nyi')


class EventSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for categories."""

    def test_visitor_is_not_able_to_add_events(self):
        # Check url only
        self.fail('nyi')

    def test_visitor_is_able_to_view_edit_form_but_not_to_change(self):
        event = self.create_event(datetime=get_datetime_today_8_32_am())
        browser = self.get_browser('cal-visitor')
        browser.open(
            'http://localhost/ab/++attribute++calendar/%s' % event.__name__)
        # There are no fields to edit and no delete button:
        self.assertEqual(['form.buttons.apply', 'form.buttons.cancel'],
                         browser.get_all_control_names())
