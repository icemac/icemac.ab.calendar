# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
import datetime
import gocept.testing.assertion
import icemac.ab.calendar
import icemac.ab.calendar.browser.calendar
import icemac.ab.calendar.category
import icemac.ab.calendar.event
import icemac.addressbook.browser.interfaces
import icemac.addressbook.testing
import icemac.addressbook.utils
import mock
import pytz
import unittest2 as unittest
import zope.publisher.browser


ZCML_LAYER = icemac.addressbook.testing.SecondaryZCMLLayer(
    'Calendar', __name__, icemac.ab.calendar,
    bases=[icemac.addressbook.testing.ZCML_LAYER])
ZODB_LAYER = icemac.addressbook.testing.ZODBLayer(
    'Calendar', ZCML_LAYER)
TEST_BROWSER_LAYER = icemac.addressbook.testing.TestBrowserLayer(
    'Calendar', ZODB_LAYER)
SELENIUM_LAYER = icemac.addressbook.testing.SeleniumLayer(
    'Calendar', ZODB_LAYER)


class TestMixIn(object):
    """Helper methods which might be useful in all tests."""

    def get_datetime(self, args=(), tzinfo=None):
        """Create a datetime object.

        `args` ... time tuple
        If no `args` are given current time is returned.
        If `tzinfo` is None, UTC is used.

        """
        if tzinfo is None:
            tzinfo = pytz.utc
        if args:
            return datetime.datetime(*args, tzinfo=tzinfo)
        return datetime.datetime.now(tz=tzinfo)

    def format_datetime(self, datetime):
        """Format a datetime to the format needed in testbrowser."""
        return datetime.strftime('%y/%m/%d %H:%M')

    def get_request(self, **kw):
        """Get a request object on the right skin layer."""
        return zope.publisher.browser.TestRequest(
            skin=icemac.addressbook.browser.interfaces.IAddressBookLayer,
            **kw)

    def get_event_description(self, time_tuple=(), **kw):
        """Get an icemac.ab.calendar.browser.calendar.EventDescription.

        time_tuple ... `now` if empty.
        **kw ... attributes to be set on the event(!).
        Does not actually create an event.

        """
        event = mock.MagicMock()
        event.datetime = self.get_datetime(time_tuple)
        for key, value in kw.items():
            setattr(event, key, value)
        ICalendarDisplaySettings = (
            'icemac.ab.calendar.interfaces.ICalendarDisplaySettings')
        get_time_zone_name = (
            'icemac.addressbook.preferences.utils.get_time_zone_name')
        with mock.patch(ICalendarDisplaySettings) as ICalendarDisplaySettings,\
                mock.patch('icemac.ab.calendar.interfaces.ICalendar'),\
                mock.patch(get_time_zone_name, return_value='UTC'):
            ICalendarDisplaySettings.event_additional_fields = ()
            return icemac.ab.calendar.browser.calendar.EventDescription(event)

    def patch_get_time_zone_name(self):
        patcher = mock.patch(
            'icemac.addressbook.preferences.utils.get_time_zone_name',
            return_value='UTC')
        patcher.start()
        self.addCleanup(patcher.stop)


class ZODBTestMixIn(object):
    """Mix-in methods for test cases using the ZODB."""

    def _create(self, class_, parent=None, **kw):
        """Helper method to create an object in the ZODB."""
        ab = self.layer['addressbook']
        if parent is None:
            parent = ab
        else:
            parent = getattr(ab, parent)
        with icemac.addressbook.utils.site(ab):
            name = icemac.addressbook.utils.create_and_add(
                parent, class_, **kw)
        return parent[name]

    def create_category(self, title):
        """Create a new event category."""
        return self._create(icemac.ab.calendar.category.Category,
                            parent='calendar_categories', title=title)

    def create_event(self, **kw):
        """Create a new event in the calendar."""
        return self._create(icemac.ab.calendar.event.Event,
                            parent='calendar', **kw)

    def create_recurring_event(self, **kw):
        """Create a new recurring event in master data."""
        return self._create(icemac.ab.calendar.event.RecurringEvent,
                            parent='calendar_recurring_events', **kw)


class UnitTestCase(unittest.TestCase, TestMixIn):
    """Test case for unittests."""


class ZCMLTestCase(unittest.TestCase, TestMixIn):
    """Test case for test which only need the ZCML registrations."""
    layer = ZCML_LAYER


class ZODBTestCase(unittest.TestCase,
                   gocept.testing.assertion.Ellipsis,
                   TestMixIn,
                   ZODBTestMixIn):
    """Test case for test which need the ZODB."""
    layer = ZODB_LAYER


class BrowserTestCase(unittest.TestCase,
                      icemac.addressbook.testing.BrowserMixIn,
                      TestMixIn,
                      ZODBTestMixIn,
                      icemac.addressbook.testing.ZODBMixIn):
    """Test case for browser tests."""
    layer = TEST_BROWSER_LAYER


class SeleniumTestCase(icemac.addressbook.testing.SeleniumTestCase):
    """Test case for selenium tests."""
    layer = SELENIUM_LAYER
