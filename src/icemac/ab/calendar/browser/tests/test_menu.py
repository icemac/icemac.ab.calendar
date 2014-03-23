from __future__ import unicode_literals
import icemac.ab.calendar.testing
import icemac.addressbook.browser.testing


class CalendarSelectedCheckerTests(
        icemac.addressbook.browser.testing.SiteMenuTestMixIn,
        icemac.ab.calendar.testing.BrowserTestCase):
    """Testing ..menu.CalendarSelectedChecker"""

    menu_item_index = 0
    menu_item_title = 'Calendar'
    menu_item_URL = 'http://localhost/ab/++attribute++calendar/'
    login_as = 'cal-editor'

    def test_calendar_tab_is_selected_on_calendar_overview(self):
        self.browser.open(self.menu_item_URL)
        self.assertIsSelected()

    def test_calendar_tab_is_not_selected_on_master_data(self):
        self.browser.open('http://localhost/ab/@@masterdata.html')
        self.assertIsNotSelected()

    def test_calendar_tab_is_selected_on_calendar_year_view(self):
        self.browser.open(
            'http://localhost/ab/++attribute++calendar/year.html')
        self.assertIsSelected()

    def test_calendar_tab_is_selected_on_event_view(self):
        event = self.create_event()
        browser = self.browser
        browser.open(
            'http://localhost/ab/++attribute++calendar/%s/@@clone.html' %
            event.__name__)
        self.assertIsSelected()
