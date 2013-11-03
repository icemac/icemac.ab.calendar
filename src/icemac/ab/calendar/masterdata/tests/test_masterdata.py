import icemac.ab.calendar.testing


class MasterDataSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for master data."""

    def test_visitor_is_able_to_access_calendar_master_data(self):
        from icemac.addressbook.testing import Browser
        browser = Browser()
        browser.login('cal-visitor')
        browser.open('http://localhost/ab')
        browser.getLink('Master data').click()
        browser.getLink('Calendar', index=1).click()
        self.assertEqual(
            'http://localhost/ab/@@calendar-masterdata.html', browser.url)
        self.assertIn('Edit calendar master data', browser.contents)

    def test_anonymous_is_not_able_to_access_calendar_master_data(self):
        from icemac.addressbook.testing import Browser
        from zope.security.interfaces import Unauthorized
        browser = Browser()
        browser.handleErrors = False  # needed to catch exception
        with self.assertRaises(Unauthorized):
            browser.open('http://localhost/ab/@@calendar-masterdata.html')
