from ..interfaces import PersonSource, ICalendarDisplaySettings, ICalendar
from icemac.addressbook.interfaces import ITitle, IKeywords
import zope.component


pytest_plugins = 'icemac.addressbook.browser.conftest'


def test_interfaces__PersonSource__getValue__1(address_book, search_data):
    """It returns all persons in address book if no `person_keyword` is set."""
    assert ([u'Hohmuth', u'Koch', u'Velleuer', u'Liebig', u'Tester, Liese'] ==
            [ITitle(x) for x in PersonSource().factory.getValues()])


def test_interfaces__PersonSource__getValue__2(address_book, search_data):
    """It returns only the persons in address book having `person_keyword`."""
    kw = zope.component.getUtility(IKeywords).get_keyword_by_title('church')
    # `search_data` yields an address_book instance which contains the person
    # data and is set as site, so we have to use it here:
    ICalendarDisplaySettings(ICalendar(search_data)).person_keyword = kw
    assert ([u'Koch', u'Velleuer', u'Liebig'] ==
            [ITitle(x) for x in PersonSource().factory.getValues()])
