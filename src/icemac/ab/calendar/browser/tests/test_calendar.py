import icemac.ab.calendar.testing


class CalendarSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for the calendar."""

    def test_visitor_is_able_to_access_the_calendar(self):
        from icemac.addressbook.testing import Browser
        from mechanize import LinkNotFoundError

        browser = Browser()
        browser.login('cal-visitor')
        browser.open('http://localhost/ab')
        browser.getLink('Calendar').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar', browser.url)
        self.assertIn('Sunday', browser.contents)
        # Cannot add events:
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('event').click()

    def test_anonymous_is_not_able_to_access_calendar(self):
        from icemac.addressbook.testing import Browser
        from zope.security.interfaces import Unauthorized
        browser = Browser()
        browser.handleErrors = False  # needed to catch exception
        with self.assertRaises(Unauthorized):
            browser.open('http://localhost/ab/++attribute++calendar')


class CalendarFTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Testing ..calendar.Calendar."""

    def setUp(self):
        from icemac.addressbook.testing import Browser
        super(CalendarFTests, self).setUp()
        self.browser = Browser()
        self.browser.login('cal-visitor')
        self.browser.open('http://localhost/ab/++attribute++calendar')

    def test_displays_current_month_by_default(self):
        import datetime
        current_month = datetime.date.today().strftime('%B %Y')
        self.assertIn(current_month, self.browser.contents)

    def test_can_switch_to_entered_month(self):
        browser = self.browser
        browser.getControl('month').value = '05/2003'
        browser.getControl('Apply').click()
        self.assertIn('May 2003', self.browser.contents)
        self.assertEqual('05/2003', browser.getControl('month').value)
        self.assertEqual(['Month changed.'], browser.get_messages())
