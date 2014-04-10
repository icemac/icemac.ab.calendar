# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from __future__ import unicode_literals
import icemac.ab.calendar.testing


class RecurringEventCRUD(icemac.ab.calendar.testing.BrowserTestCase):
    """CRUD testing for ..event.*"""

    def setUp(self):
        super(RecurringEventCRUD, self).setUp()
        self.create_category('birthday')
        self.browser = self.get_browser('cal-editor')
        self.browser.open(
            'http://localhost/ab/++attribute++calendar_recurring_events')

    def test_navigation_to_recurring_event_edit_is_possible(self):
        self.browser.open('http://localhost/ab')
        self.browser.getLink('Master data').click()
        self.browser.getLink('Calendar', index=1).click()
        self.assertEqual('http://localhost/ab/@@calendar-masterdata.html',
                         self.browser.url)
        self.browser.getLink('Recurring Events').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar_recurring_events',
            self.browser.url)
        self.assertIn(
            'No recurring events defined yet.', self.browser.contents)

    def test_recurring_events_can_be_added_and_is_shown_in_list(self):
        self.browser.getLink('recurring event').click()
        self.browser.getControl('event category').getControl(
            'birthday').selected = True
        self.browser.getControl('datetime').value = self.format_datetime(
            self.get_datetime())
        self.browser.getControl(name='form.buttons.add').click()
        self.assertEqual(['"birthday" added.'], self.browser.get_messages())
        # New recurring event shows up in list:
        self.assertIn('birthday', self.browser.contents)

    def test_recurring_event_can_be_edited(self):
        self.create_recurring_event(
            alternative_title='wedding day', datetime=self.get_datetime())
        self.browser.reload()
        self.browser.getLink('wedding day').click()
        self.assertEqual(
            'wedding day', self.browser.getControl('alternative title').value)
        self.browser.getControl('alternative title').value = ''
        self.browser.getControl('event category').getControl(
            'birthday').selected = True
        self.browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], self.browser.get_messages())
        # Changed event name shows up in list:
        self.assertIn('birthday', self.browser.contents)

    def test_recurring_event_can_be_deleted(self):
        self.create_recurring_event(
            alternative_title='birthday', datetime=self.get_datetime())
        self.browser.reload()
        self.browser.getLink('birthday').click()
        self.browser.getControl('Delete').click()
        self.assertIn('Do you really want to delete this recurring event?',
                      self.browser.contents)
        self.browser.getControl('Yes').click()
        self.assertEqual(['"birthday" deleted.'], self.browser.get_messages())


class RecurringEventSecurity(icemac.ab.calendar.testing.BrowserTestCase):
    """Security tests for recurring events."""

    def test_visitor_is_able_to_see_recurring_events_but_cannot_change_them(
            self):
        from mechanize import LinkNotFoundError

        self.create_recurring_event(alternative_title='birthday')
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/@@calendar-masterdata.html')
        browser.handleErrors = False
        browser.getLink('Recurring Events').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar_recurring_events',
            browser.url)
        # There is no add link:
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('recurring event').click()
        browser.getLink('birthday').click()
        # There are no fields and no delete button:
        self.assertEqual(['form.buttons.apply', 'form.buttons.cancel'],
                         browser.get_all_control_names())

    def test_anonymous_is_not_able_to_access_recurring_events(self):
        from zope.security.interfaces import Unauthorized
        browser = self.get_browser()
        browser.handleErrors = False  # needed to catch exception
        with self.assertRaises(Unauthorized):
            browser.open(
                'http://localhost/ab/++attribute++calendar_recurring_events')
