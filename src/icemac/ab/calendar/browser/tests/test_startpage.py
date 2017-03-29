import pytest


@pytest.mark.webdriver
def test_startpage__calendar__1_webdriver(address_book, webdriver):
    """It redirects to the calendar if this is set on the address book."""
    ab = webdriver.address_book
    webdriver.login('mgr', ab.ADDRESS_BOOK_EDIT_URL)
    ab.startpage = 'Calendar'
    ab.submit('apply')
    webdriver.open(ab.ADDRESS_BOOK_DEFAULT_URL)
    assert webdriver.calendar.CALENDAR_MONTH_OVERVIEW_URL == webdriver.path
