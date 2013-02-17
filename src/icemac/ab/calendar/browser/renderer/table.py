# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt
from .base import Calendar
from .interfaces import AUSFALL, INTERN
import datetime


SPECIAL_CLASS_MAPPING = {
    True: 'red',
    AUSFALL: 'gray',
    INTERN: '',
    }


def render_event(event, show_datetime):
    result = []
    if show_datetime:
        if not event.whole_day: # and event.has_text():
            format_string = '%H:%M Uhr'
        else:
            format_string = ''
        result.append('  <dt>%s</dt>' % (
            event.datetime.strftime(format_string)))
    result.append('  <dd')
    css_class = SPECIAL_CLASS_MAPPING.get(event.special_event)
    if css_class:
        result.append('    class="%s"' % css_class)
    result.append('  >%s</dd>' % event.getText())
    return '\n'.join(result)


class Table(Calendar):
    """Tablular display of a calendar."""

    def __init__(self, *args, **kw):
        super(Table, self).__init__(*args, **kw)
        first_of_month = self.month.firstOfMonth()
        if first_of_month.isoweekday() == 7:
            self.first_table_day = first_of_month
        else:
            self.first_table_day = (
                first_of_month - datetime.timedelta(
                    first_of_month.isoweekday()))
        end_of_month = self.month.lastOfMonth()
        self.num_of_days = (end_of_month - self.first_table_day).days + 1
        if end_of_month.isoweekday() == 7:
            self.num_of_days += 6
        else:
            self.num_of_days += 6 - end_of_month.isoweekday()

    def table_head(self):
        self.write('<h2>%s</h2>', self.month.firstOfMonth().strftime('%B %Y'))
        self.write('<table class="calendar">')
        self.write('  <thead>')
        self.write('    <tr>')
        for delta in range(7):
            day = self.first_table_day + datetime.timedelta(delta)
            day_name = day.strftime('%A')
            self.write('      <th class="%s">%s</th>', day_name, day_name)
        self.write('    </tr>')
        self.write('  </thead>')

    def render(self):
        self.table_head()
        self.write('  <tbody>')
        events = self.sort_events(self.clean_events(self.month_events()))
        for delta in xrange(self.num_of_days):
            if (delta % 7) == 0:
                # week start
                self.write('    <tr>')
            if (delta + 1 % 7) == 0:
                # week end
                self.write('    </tr>')
            day = self.first_table_day + datetime.timedelta(delta)
            prev_datetime = None
            self.write('<td class="%s">', day.strftime('%A'))
            if day in self.month:
                self.write('<span>%s</span>', day.day)
                found_events_for_day = False
                for ev in events[:]:
                    if ev.datetime.date() != day:
                        # events are sorted, so we can break on day in future
                        break
                    # remove day from list to print to keep for loop short
                    events.pop(events.index(ev))
                    if not found_events_for_day:
                        self.write('<dl>')
                        found_events_for_day = True
                    self.write(render_event(ev, ev.datetime!=prev_datetime))
                    prev_datetime = ev.datetime
                if found_events_for_day:
                    self.write('</dl>')
            self.write('</td>')

        self.write('  </tbody>')
        self.write('</table>')
        return self.fd.getvalue()
