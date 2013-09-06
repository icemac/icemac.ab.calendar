import icemac.ab.calendar.testing


class CalendarTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Testing ..calendar.Calendar."""

    def setUp(self):
        from icemac.addressbook.testing import create_field
        super(CalendarTests, self).setUp()
        create_field(
            self.layer['addressbook'], 'icemac.ab.calendar.event.Event',
            u'Int', u'reservations')

    def test_fields_for_display_can_be_selected(self):
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab/@@calendar-masterdata.html')
        browser.getLink('Calendar view').click()
        self.assertEqual(
            'http://localhost/ab/++attribute++calendar/@@edit-display.html',
            browser.url)
        browser.in_out_widget_select('form.widgets.event_additional_fields',
                                     [browser.getControl('persons'),
                                      browser.getControl('reservations')])
        browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], browser.get_messages())


class CalendarSecurityTests(icemac.ab.calendar.testing.BrowserTestCase):
    """Security testing ..calendar.Calendar."""

    def test_visitor_is_not_able_to_access_display_fields(self):
        from mechanize import LinkNotFoundError, HTTPError
        browser = self.get_browser('cal-visitor')
        browser.open('http://localhost/ab/@@calendar-masterdata.html')
        with self.assertRaises(LinkNotFoundError):
            browser.getLink('Calendar view')
        # The URL is not accesible, too:
        with self.assertRaises(HTTPError) as err:
            browser.open('http://localhost/ab/++attribute++calendar/'
                         '@@edit-display.html')
        self.assertEqual('HTTP Error 403: Forbidden', str(err.exception))
