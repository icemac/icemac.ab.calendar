import icemac.ab.calendar.testing


class CalendarTests(icemac.ab.calendar.testing.BrowserTestCase):

    """Testing ..calendar.Calendar."""

    def setUp(self):
        from icemac.addressbook.testing import create_field
        super(CalendarTests, self).setUp()
        self.ab = self.layer['addressbook']
        self.field_name = create_field(
            self.ab, 'icemac.ab.calendar.event.Event', u'Int', u'reservations')

    def assert_fields_selected(self, fields, browser):
        self.assertEqual(
            fields,
            browser.getControl(
                name='form.widgets.event_additional_fields.to').displayOptions)

    def test_fields_for_display_can_be_selected(self):
        from icemac.ab.calendar.interfaces import IEvent
        from icemac.addressbook.interfaces import IEntity
        from icemac.addressbook.utils import site
        browser = self.get_browser('cal-editor')
        browser.open('http://localhost/ab/@@calendar-masterdata.html')
        browser.getLink('Calendar view').click()
        edit_display_URL = (
            'http://localhost/ab/++attribute++calendar/@@edit-display.html')
        self.assertEqual(edit_display_URL, browser.url)
        browser.in_out_widget_select('form.widgets.event_additional_fields',
                                     [browser.getControl('persons'),
                                      browser.getControl('reservations')])
        browser.getControl('Apply').click()
        self.assertEqual(
            ['Data successfully updated.'], browser.get_messages())
        browser.open(edit_display_URL)
        self.assert_fields_selected(['reservations', 'persons'], browser)
        # Does not break on selected but deleted user defined field:
        with site(self.ab):
            event_entity = IEntity(IEvent)
            event_entity.removeField(event_entity.getRawField(self.field_name))
        browser.open(edit_display_URL)
        self.assert_fields_selected(['persons'], browser)


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
