# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt
from .base import Calendar
from .interfaces import AUSFALL, INTERN
from icemac.addressbook.i18n import _
import datetime
import grokcore.component as grok
import icemac.addressbook.browser.base
import zope.component


SPECIAL_CLASS_MAPPING = {
    True: 'red',
    AUSFALL: 'gray',
    INTERN: '',
    }


class TableEvent(icemac.addressbook.browser.base.BaseView):
    """View to render an event in the table."""

    show_time = True
    action_class = 'edit'
    action_link = _('Edit')

    def time(self):
        if self.context.whole_day: # and not event.has_text():
            return ''
        formatter = self.request.locale.dates.getFormatter('time', 'full')
        # Only the length 'full' has 'Uhr' in it, but it contains the
        # timezone offset too which we do not want to display here:
        time= ' '.join(formatter.format(self.context.datetime).split(' ')[:-1])
        return time

    def dd_class(self):
        return SPECIAL_CLASS_MAPPING.get(self.context.special_event)

    def text(self):
        return self.context.getText()

    def action_url(self):
        return self.url(self.context.context)


class Table(Calendar):
    """Tabular display of a calendar."""

    grok.name('table')

    def update(self):
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
                self.write('<span class="number">%s</span>', day.day)
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
                    view = zope.component.getMultiAdapter(
                        (ev, self.request), name='table-event')
                    view.show_time = (ev.datetime != prev_datetime)
                    self.write(view())
                    prev_datetime = ev.datetime
                if found_events_for_day:
                    self.write('</dl>')
            self.write('</td>')

        self.write('  </tbody>')
        self.write('</table>')
        return self.fd.getvalue()


