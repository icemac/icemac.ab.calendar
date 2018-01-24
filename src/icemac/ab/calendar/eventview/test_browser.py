def test_browser__Table__1(address_book, browser):
    """It renders a message if there are no event views configured, yet."""
    browser.login('mgr')
    browser.open(browser.CALENDAR_MASTERDATA_URL)
    browser.getLink('Event views').click()
    assert browser.url == browser.CALENDAR_MASTERDATA_EVENTVIEW_URL
    assert 'No event views defined yet.' in browser.contents
