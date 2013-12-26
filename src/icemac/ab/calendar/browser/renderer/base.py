# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
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

    def month_events(self):
        # events = []
        # for event in self.events:
        #     if isinstance(event, Event):
        #         events.append(event)
        #     else:
        #         if self.only_single_events:
        #             continue
        #         for ev in event.create_events(self.month):
        #             events.append(ev)
        # return events
        return self.events

    @property
    def max_date(self):
        "Date of the most future single event."
        return sorted([x.date
                       for x in self.events
                       if isinstance(x, Event)],
                      reverse=True)[0]

    def clean_events(self, events):
        result = []
        for event in events[:]:
            if event.datetime not in self.month:
                continue
            competitor_events = [ev for ev in events
                                 if (ev != event and
                                     ev.kind == event.kind and
                                     ev.datetime == event.datetime)]
            if any([ev.prio > event.prio for ev in competitor_events]):
                continue
            result.append(event)
        return result

    def sort_events(self, events):
        return sorted(
            events,
            key=lambda ev: tuple(ev.datetime.timetuple())[:5] + (ev.prio,))

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
