import icemac.addressbook.testing


class JSLintTest(icemac.addressbook.testing.JSLintTest):

    include = (
        'icemac.ab.calendar.browser:resources',
    )
