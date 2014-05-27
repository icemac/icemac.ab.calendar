import icemac.ab.calendar.testing


class StartpageDispatchSTests(icemac.ab.calendar.testing.SeleniumTestCase):
    """Selenium testing ..startpage.calendar."""

    def test_startpage_redirects_to_calendar_if_set_on_address_book(self):
        self.login()
        sel = self.selenium
        sel.open('/ab/@@edit-address_book.html')
        sel.select('id=form-widgets-startpage', 'label=Calendar')
        sel.type('id=form-widgets-title', 'Test')
        sel.clickAndWait('id=form-buttons-apply')
        sel.open('/ab')
        sel.assertLocation(
            'http://%s/ab/++attribute++calendar/@@month.html' % sel.server)
