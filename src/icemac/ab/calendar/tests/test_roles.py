import icemac.ab.calendar.testing


class RoleTests(icemac.ab.calendar.testing.ZCMLTestCase):
    """Testing ..roles."""

    def test_calendar_editor_is_in_editor_roles(self):
        from icemac.addressbook.principals.roles import has_editor_role
        self.assertTrue(has_editor_role(['icemac.ab.calendar.Editor']))

    def test_calendar_visitor_is_in_visitor_roles(self):
        from icemac.addressbook.principals.roles import has_visitor_role
        self.assertTrue(has_visitor_role(['icemac.ab.calendar.Visitor']))
