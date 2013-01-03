# -*- coding: utf-8 -*-
# Copyright (c) 2010, 2013 Michael Howitz
# See also LICENSE.txt
import datetime


def last_of_month(date):
    """Last day of the month `date` belongs to."""
    if date.month == 12:
        month = 1
        year = date.year + 1
    else:
        month = date.month + 1
        year = date.year
    return datetime.date(year, month, 1) - datetime.timedelta(1)


class Calendar(object):
    """Base of calendar view."""

    def __init__(self, month, events, fd, only_single_events=False):
        self.month = month
        self.events = events
        self.fd = fd
        self.only_single_events = only_single_events

    def month_events(self):
        events = []
        for event in self.events:
            if isinstance(event, Event):
                events.append(event)
            else:
                if self.only_single_events:
                    continue
                for ev in event.create_events(self.month):
                    events.append(ev)
        return events

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
            if not (event.datetime.month == self.month.month and
                    event.datetime.year == self.month.year):
                continue
            competitor_events = [ev for ev in events
                                 if (ev != event and
                                     ev.id == event.id and
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
