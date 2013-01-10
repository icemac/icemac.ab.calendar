# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import icemac.ab.calendar
import icemac.addressbook.testing


ZCML_LAYER = icemac.addressbook.testing.ZCMLLayer(
    'Calendar', __name__, icemac.ab.calendar,
    bases=[icemac.addressbook.testing.ZCML_LAYER])
ZODB_LAYER = icemac.addressbook.testing.ZODBLayer(
    'Calendar', ZCML_LAYER)
TEST_BROWSER_LAYER = icemac.addressbook.testing.TestBrowserLayer(
    'Calendar', ZODB_LAYER)
