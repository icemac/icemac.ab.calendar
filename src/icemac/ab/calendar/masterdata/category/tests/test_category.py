# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import icemac.ab.calendar.testing
import unittest2 as unittest


class CategoryCRUD(icemac.ab.calendar.testing.BrowserTestCase):
    """CRUD testing for ..category.*"""

    def setUp(self):
        from icemac.addressbook.testing import Browser
        super(CategoryCRUD, self).setUp()
        self.browser = Browser()
        self.browser.login('mgr')
        self.browser.handleErrors = False
        self.browser.open(
            'http://localhost/ab/++attribute++calendar_categories')

    def test_navigation_to_category_edit_is_possible(self):
        self.browser.open('http://localhost/ab')
        self.browser.getLink('Master data').click()
        self.browser.getLink('Calendar', index=1).click()
        self.assertEqual('http://localhost/ab/@@calendar-masterdata.html',
                         self.browser.url)
        self.browser.getLink('Event categories').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar_categories',
            self.browser.url)
        self.assertIn('No event categories defined yet.', self.browser.contents)

    def test_category_can_be_added_and_is_shown_in_list(self):
        from icemac.addressbook.testing import get_messages
        self.browser.getLink('event category').click()
        self.browser.getControl('event category').value = 'birthday'
        self.browser.getControl('Add').click()
        self.assertEqual(['"birthday" added.'], get_messages(self.browser))
        # New category show up in list:
        self.assertIn('birthday', self.browser.contents)

    def test_category_can_be_edited(self):
        self.create_category(u'birthday')
        self.browser.reload()
        self.browser.getLink('birthday').click()
        self.assertEqual(
            'birthday', self.browser.getControl('event category').value)
        self.browser.getControl('event category').value = 'wedding day'
        self.browser.getControl('Apply').click()
        from icemac.addressbook.testing import get_messages
        self.assertEqual(
            ['Data successfully updated.'], get_messages(self.browser))
        # Changed category name show up in list:
        self.assertIn('wedding day', self.browser.contents)

    # def test_new_category_with_existing_title_cannot_be_added(self):
    #     self.fail('nyi')

    # def test_new_category_title_cannot_be_changed_to_existing_one(self):
    #     self.fail('nyi')

    # def test_category_can_be_deleted(self):
    #     self.fail('nyi')

    # def test_used_category_cannot_be_deleted(self):
    #     self.fail('nyi')
