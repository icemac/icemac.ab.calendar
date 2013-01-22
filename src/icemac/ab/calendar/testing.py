# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import icemac.ab.calendar
import icemac.ab.calendar.category
import icemac.ab.calendar.event
import icemac.addressbook.testing
import icemac.addressbook.utils
import unittest2 as unittest


ZCML_LAYER = icemac.addressbook.testing.ZCMLLayer(
    'Calendar', __name__, icemac.ab.calendar,
    bases=[icemac.addressbook.testing.ZCML_LAYER])
ZODB_LAYER = icemac.addressbook.testing.ZODBLayer(
    'Calendar', ZCML_LAYER)
TEST_BROWSER_LAYER = icemac.addressbook.testing.TestBrowserLayer(
    'Calendar', ZODB_LAYER)


class ZODBTestMixIn(object):
    """Mix-in methods for test cases using the ZODB."""

    def _create(self, class_, parent=None, **kw):
        """Helper method to create an object in the ZODB."""
        ab = self.layer['addressbook']
        if parent is None:
            parent = ab
        else:
            parent = getattr(ab, parent)
        name = icemac.addressbook.utils.create_and_add(parent, class_, **kw)
        return parent[name]

    def create_category(self, title):
        """Create a new event category."""
        return self._create(icemac.ab.calendar.category.Category,
                            parent='calendar_categories', title=title)

    def create_event(self, **kw):
        """Create a new event in the calendar."""
        return self._create(icemac.ab.calendar.event.Event,
                            parent='calendar', **kw)


class ZCMLTestCase(unittest.TestCase):
    """Test case for test which only need the ZCML registrations."""
    layer = ZCML_LAYER


class ZODBTestCase(unittest.TestCase, ZODBTestMixIn):
    """Test case for test which need the ZODB."""
    layer = ZODB_LAYER


class BrowserTestCase(unittest.TestCase, ZODBTestMixIn):
    """Test case for browser tests."""
    layer = TEST_BROWSER_LAYER
