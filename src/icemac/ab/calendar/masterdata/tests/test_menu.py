# Copyright (c) 2014 Michael Howitz
# See also LICENSE.txt
from __future__ import unicode_literals
import icemac.ab.calendar.testing
import icemac.addressbook.browser.testing


class MasterDataSelectedCheckerTests(
        icemac.addressbook.browser.testing.SiteMenuTestMixIn,
        icemac.ab.calendar.testing.BrowserTestCase):
    """Testing ..menu.calendar_views"""

    menu_item_index = 4
    menu_item_title = 'Master data'
    menu_item_URL = 'http://localhost/ab/@@calendar-masterdata.html'
    login_as = 'mgr'

    def test_master_data_tab_is_selected_on_calendar_master_data_overview(
            self):
        self.browser.open(self.menu_item_URL)
        self.assertIsSelected()

    def test_master_data_tab_is_selected_on_event_categories(self):
        self.browser.open(
            'http://localhost/ab/++attribute++calendar_categories')
        self.assertIsSelected()

    def test_master_data_tab_is_selected_on_edit_display(self):
        self.browser.open(
            'http://localhost/ab/++attribute++calendar/@@edit-display.html')
        self.assertIsSelected()
