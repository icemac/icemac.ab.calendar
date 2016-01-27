def test_resource__1(address_book, browser):
    """calender_view_renders_calender_css."""
    browser.login('cal-visitor')
    browser.open(browser.CALENDAR_MONTH_OVERVIEW_URL)
    assert '/fanstatic/calendar/calendar.css' in browser.contents


def test_resource__2(address_book, browser):
    """event_add_form_renders_calender_css."""
    browser.login('cal-editor')
    browser.open(browser.EVENT_ADD_URL)
    assert '/fanstatic/calendar/calendar.css' in browser.contents
