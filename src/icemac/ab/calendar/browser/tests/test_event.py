import icemac.ab.calendar.testing


class EventCRUD(icemac.ab.calendar.testing.BrowserTestCase):
    """CRUD testing for ..event.*"""

    def setUp(self):
        from datetime import date, time, datetime
        from icemac.addressbook.testing import Browser
        from pytz import utc
        super(EventCRUD, self).setUp()
        self.create_category(u'birthday')
        self.create_category(u'wedding day')
        self.datetime = datetime.combine(date.today(), time(8, 32, tzinfo=utc))
        self.formatted_datetime = self.datetime.strftime('%y/%m/%d %H:%M')
        self.browser = Browser()
        self.browser.login('cal-editor')
        self.browser.open('http://localhost/ab/++attribute++calendar')

    def test_navigation_to_calendar_is_possible(self):
        self.browser.open('http://localhost/ab')
        self.browser.getLink('Calendar').click()
        self.assertEqual('http://localhost/ab/++attribute++calendar',
                         self.browser.url)

    def test_event_can_be_added_and_is_shown_in_calendar(self):
        from icemac.addressbook.testing import get_messages
        self.browser.getLink('event').click()
        self.browser.getControl(
            'date and time').value = self.formatted_datetime
        self.browser.getControl(
            'event category').displayValue = ['wedding day']
        self.browser.getControl('Add', index=1).click()
        self.assertEqual('http://localhost/ab/++attribute++calendar',
                         self.browser.url)
        self.assertEqual(
            ['"wedding day" added.'], get_messages(self.browser))
        # New event shows up in calendar:
        self.assertIn('08:32', self.browser.contents)

    def test_event_can_be_edited(self):
        event = self.create_event(datetime=self.datetime)
        browser = self.browser
        browser.reload()
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

    def test_visitor_is_not_able_to_edit_events(self):
        # Check url only
        self.fail('nyi')
