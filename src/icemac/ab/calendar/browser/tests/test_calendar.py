import icemac.ab.calendar.testing


class CalendarSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for the calendar."""

    def test_visitor_is_able_to_access_the_calendar(self):
        from datetime import date
        from icemac.addressbook.testing import Browser
        from mechanize import LinkNotFoundError

        browser = Browser()
        browser.login('cal-visitor')
        browser.open('http://localhost/ab')
        browser.getLink('Calendar').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar', browser.url)
        self.assertIn(date.today().strftime('%B %Y'), browser.contents)
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

