def test_startpage__calendar__1(address_book, webdriver):
    """It redirects to the calendar if this is set on the address book."""
    sel = webdriver.login('mgr')
    sel.open('/ab/@@edit-address_book.html')
    sel.select('id=form-widgets-startpage', 'label=Calendar')
    sel.clickAndWait('id=form-buttons-apply')
    sel.open('/ab')
    assert sel.getLocation().endswith('/ab/++attribute++calendar/@@month.html')
