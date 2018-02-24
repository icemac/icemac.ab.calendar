from __future__ import unicode_literals
from .interfaces import EventViewConfigurationSource


def test_interface__EventViewConfigurationSource__getValue__1(
        address_book, AddressBookFactory, EventViewConfigurationFactory):
    """It returns all created EventViewConfiguration objects of the site.

    The values are returned alphabetically sorted by the title of the
    EventViewConfiguration objects.
    """
    evc2 = EventViewConfigurationFactory(address_book, '2 weeks')
    evc1 = EventViewConfigurationFactory(address_book, '1 week')
    evc3 = EventViewConfigurationFactory(address_book, '3 weeks')
    ab2 = AddressBookFactory('ab2')
    EventViewConfigurationFactory(ab2, '1 month')
    source = EventViewConfigurationSource().factory
    assert [evc1, evc2, evc3] == list(source.getValues())


def test_interface__EventViewConfigurationSource__getTitle__1(
        address_book, EventViewConfigurationFactory):
    """It returns the title of the EventViewConfiguration."""
    evc = EventViewConfigurationFactory(address_book, '2 weeks')
    source = EventViewConfigurationSource().factory
    assert '2 weeks' == source.getTitle(evc)
