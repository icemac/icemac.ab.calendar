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


class BrowserTestCase(unittest.TestCase):
    """Test case for browser tests."""
    layer = TEST_BROWSER_LAYER

    def create_category(self, title):
        ab = self.layer['addressbook']
        parent = ab.calendar_categories
        return icemac.addressbook.utils.create_and_add(
            parent, icemac.ab.calendar.category.Category, title=title)
