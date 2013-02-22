# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt
from cStringIO import StringIO
import datetime
import gocept.month


class Calendar(object):
    """Base of calendar view."""

    # XXX make me a multi adapter for (month, request),
    # Adapter can get the events from the calendar utility.
    def __init__(self, request, month, events, fd=None, only_single_events=False):
        self.request = request
        self.month = month
        self.events = events
        if fd is None:
            # XXX Is there a case where we really want fd to be not None?
            fd = StringIO()
        self.fd = fd
        self.only_single_events = only_single_events

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
        self.fd.write("%s\n" % (string.encode('utf-8') % args))

    def render(self):
        raise NotImplementedError
