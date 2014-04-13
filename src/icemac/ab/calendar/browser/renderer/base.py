# -*- coding: utf-8 -*-
# Copyright (c) 2010-2014 Michael Howitz
# See also LICENSE.txt
from cStringIO import StringIO
import gocept.month
import grokcore.component as grok
import icemac.ab.calendar.browser.renderer.interfaces
import icemac.addressbook.browser.interfaces


class Calendar(grok.MultiAdapter):
    """Base of calendar view."""

    grok.baseclass()
    grok.adapts(
        gocept.month.IMonth,
        icemac.addressbook.browser.interfaces.IAddressBookLayer,
        list)
    grok.implements(icemac.ab.calendar.browser.renderer.interfaces.IRenderer)

    def __init__(self, month, request, events):
        self.request = request
        self.month = month
        self.events = events
        self._fd = StringIO()

    @property
    def max_date(self):
        "Date of the most future single event."
        return sorted([x.date
                       for x in self.events
                       if isinstance(x, Event)],
                      reverse=True)[0]

    def write(self, string, *args):
        """Store a string which might contain % marks which get replaced."""
        text = string % args
        # We have to encode the text here as the used cStringIO does not
        # support unicode charaters outside ASCII:
        self._fd.write(text.encode('utf-8'))
        self._fd.write('\n')

    def read(self):
        """Get the stored information back as unicode."""
        return self._fd.getvalue().decode('utf-8')

    def update(self):
        pass

    def render(self):
        raise NotImplementedError()

    def __call__(self):
        self.update()
        return self.render()
