# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt

import icemac.ab.importer.browser
import icemac.addressbook.testing
import plone.testing.zca


CALENDAR_ZCML_LAYER = plone.testing.zca.ZCMLSandbox(
    name="CalendarZCML", filename="ftesting.zcml",
    package=icemac.ab.calendar.browser)


# XXX refactor in icemac.addressbook to a factory + use in i.ab.importer, too
CalendarLayer = icemac.addressbook.testing._WSGITestBrowserLayer(
    bases=[icemac.addressbook.testing.WSGILayer(
        bases=[icemac.addressbook.testing._ZODBIsolatedTestLayer(
            bases=[icemac.addressbook.testing._ZODBLayer(
                bases=[icemac.addressbook.testing.ZCML_LAYER,
                       IMPORTER_ZCML_LAYER],
                name='CalendarZODBLayer')],
            name='CalendarZODBIsolatedTestLayer')],
        name='CalendarWSGILayer')],
    name='CalendarLayer')
