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
        self.browser.login('cal-editor')
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
        from icemac.addressbook.testing import get_messages
        self.create_category(u'birthday')
        self.browser.reload()
        self.browser.getLink('birthday').click()
        self.assertEqual(
            'birthday', self.browser.getControl('event category').value)
        self.browser.getControl('event category').value = 'wedding day'
        self.browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], get_messages(self.browser))
        # Changed category name show up in list:
        self.assertIn('wedding day', self.browser.contents)

    def test_new_category_with_existing_title_cannot_be_added(self):
        self.create_category(u'birthday')
        self.browser.getLink('event category').click()
        self.browser.getControl('event category').value = 'birthday'
        self.browser.getControl('Add').click()
        self.assertIn('There were some errors.', self.browser.contents)
        self.assertIn('This category already exists.', self.browser.contents)

    def test_category_title_cannot_be_changed_to_existing_one(self):
        self.create_category(u'birthday')
        self.create_category(u'wedding day')
        self.browser.reload()
        self.browser.getLink('birthday').click()
        self.browser.getControl('event category').value = 'wedding day'
        self.browser.getControl('Apply').click()
        self.assertIn('There were some errors.', self.browser.contents)
        self.assertIn('This category already exists.', self.browser.contents)

    def test_category_can_be_deleted(self):
        self.create_category(u'birthday')
        self.browser.reload()
        self.browser.getLink('birthday').click()
        self.browser.getControl('Delete').click()

    def test_used_category_cannot_be_deleted(self):
        self.fail('nyi')


class CategorySecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for categories."""

    def test_visitor_is_able_to_see_categories_but_cannot_change_them(self):
        from icemac.addressbook.testing import Browser
        from mechanize import LinkNotFoundError

        self.create_category(u'birthday')
        browser = Browser()
        browser.login('cal-visitor')
        browser.open('http://localhost/ab/@@calendar-masterdata.html')
        browser.getLink('Event categories').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar_categories',
            browser.url)
        # There is no add link:
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('event category').click()
        browser.getLink('birthday').click()
        # There are no fields and no delete button:
        self.assertEqual(['form.buttons.apply', 'form.buttons.cancel'],
                         browser.get_all_control_names())

    def test_anonymous_is_not_able_to_access_categories(self):
        from icemac.addressbook.testing import Browser
        from zope.security.interfaces import Unauthorized
        browser = Browser()
        browser.handleErrors = False  # needed to catch exception
        with self.assertRaises(Unauthorized):
            browser.open(
                'http://localhost/ab/++attribute++calendar_categories')