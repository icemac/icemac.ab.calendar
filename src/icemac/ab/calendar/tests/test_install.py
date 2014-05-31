# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt

import icemac.ab.calendar.install
import icemac.ab.calendar.testing
import icemac.addressbook.addressbook
import icemac.addressbook.testing
import unittest2 as unittest


class TestInstall(unittest.TestCase,
                  icemac.addressbook.testing.InstallationAssertions):

    layer = icemac.ab.calendar.testing.ZODB_LAYER

    def check_addressbook(self, ab):
        self.assertAttribute(
            ab, 'calendar', icemac.ab.calendar.interfaces.ICalendar)
        self.assertAttribute(
            ab, 'calendar_categories',
            icemac.ab.calendar.interfaces.ICategories)
        self.assertAttribute(
            ab, 'calendar_recurring_events',
            icemac.ab.calendar.interfaces.IRecurringEvents)

    def setUp(self):
        self.ab = self.layer['addressbook']

    def test_create(self):
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            self.ab)
        icemac.ab.calendar.install.install_calendar(
            icemac.addressbook.addressbook.AddressBookCreated(self.ab))
        self.check_addressbook(self.ab)

    def test_recall_create(self):
        icemac.addressbook.addressbook.create_address_book_infrastructure(
            self.ab)
        event = icemac.addressbook.addressbook.AddressBookCreated(self.ab)
        icemac.ab.calendar.install.install_calendar(event)
        icemac.ab.calendar.install.install_calendar(event)
        self.check_addressbook(self.ab)
