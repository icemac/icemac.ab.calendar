# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import icemac.ab.calendar
import icemac.ab.calendar.category
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


class TestMixIn(object):
    """Mix-in methods for test cases."""

    def create_category(self, title):
        """Create a new event category."""
        ab = self.layer['addressbook']
        parent = ab.calendar_categories
        return icemac.addressbook.utils.create_and_add(
            parent, icemac.ab.calendar.category.Category, title=title)


class ZCMLTestCase(unittest.TestCase, TestMixIn):
    """Test case for test which only need the ZCML registrations."""
    layer = ZCML_LAYER


class ZODBTestCase(unittest.TestCase, TestMixIn):
    """Test case for test which need the ZODB."""
    layer = ZODB_LAYER


class BrowserTestCase(unittest.TestCase, TestMixIn):
    """Test case for browser tests."""
    layer = TEST_BROWSER_LAYER
