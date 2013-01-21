import icemac.ab.calendar.testing


class EventCRUD(icemac.ab.calendar.testing.BrowserTestCase):
    """CRUD testing for ..event.*"""

    def setUp(self):
        from icemac.addressbook.testing import Browser
        super(EventCRUD, self).setUp()
        self.create_category(u'birthday')
        self.create_category(u'wedding day')
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
        self.browser.handleErrors = False
        self.browser.getLink('event').click()
        self.browser.getControl('date and time').value = '12/01/17 16:32'
        self.browser.getControl('event category').displayValue = ['wedding day']
        self.browser.getControl('Add', index=1).click()
        self.assertEqual(
            ['"wedding day" added.'], get_messages(self.browser))
        # New event shows up in calendar:
        self.assertIn('birthday', self.browser.contents)

    def test_event_can_be_edited(self):
        pass

    def test_event_can_be_deleted(self):
        pass


class EventSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for categories."""
