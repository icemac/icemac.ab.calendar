import icemac.ab.calendar.testing


class ResourceTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Testing rendering of resources."""

    def test_calender_view_renders_calender_css(self):
        browser = self.get_browser('cal-visitor')
        browser.handleErrors = False

        browser.open('http://localhost/ab/++attribute++calendar')
        self.assertIn('calendar_css/calendar.css', browser.contents)

    def test_event_add_form_renders_calender_css(self):
        browser = self.get_browser('cal-editor')
        browser.open(
            'http://localhost/ab/++attribute++calendar/@@addEvent.html')
        self.assertIn('calendar_css/calendar.css', browser.contents)
