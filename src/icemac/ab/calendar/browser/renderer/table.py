# -*- coding: utf-8 -*-
# Copyright (c) 2010-2014 Michael Howitz
# See also LICENSE.txt
from __future__ import unicode_literals
from .base import Calendar
from .interfaces import AUSFALL, INTERN, UnknownLanguageError
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
    _action_url = None

    def time(self):
        if self.context.whole_day:  # and not event.has_text():
            return ''
        formatter = self.request.locale.dates.getFormatter(
            'time', 'short')
        time = formatter.format(self.context.datetime)
        if self.request.locale.id.language == 'de':
            time += ' Uhr'
        return time

    def dd_class(self):
        return SPECIAL_CLASS_MAPPING.get(self.context.special_event)

    def _localized(self, func):
        locale = self.request.locale
        try:
            result = func(locale.getLocaleID())
        except UnknownLanguageError:
            # No hypenation dict for the locale id (e. g. de_DE):
            try:
                # Try only the language name:
                result = func(locale.id.language)
            except UnknownLanguageError:
                # Disable hypenation for unknown languages:
                result = func()
        return result

    def text(self):
        text = self._localized(self.context.getText).strip()
        if not text:
            text = _('Edit')  # allow at least to edit the entry
        return text

    def info(self):
        return [{'info': x} for x in self._localized(self.context.getInfo)]

    def action_url(self):
        if self._action_url is None:
            self._action_url = self.url(self.context.context)
        return self._action_url


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
        calendar = self.request.locale.dates.calendars['gregorian']
        self.write('<table>')
        self.write('  <thead>')
        self.write('    <tr>')
        day_names = calendar.getDayNames()
        # Move Sunday to position one
        day_names.insert(0, day_names.pop(-1))
        for index, day_name in enumerate(day_names):
            self.write('      <th class="day-%s">%s</th>', index, day_name)
        self.write('    </tr>')
        self.write('  </thead>')

    def render(self):
        self.table_head()
        self.write('  <tbody>')
        today = datetime.date.today()
        events = self.events
        for delta in xrange(self.num_of_days):
            if (delta % 7) == 0:
                # week start
                self.write('    <tr>')
            if (delta + 1 % 7) == 0:
                # week end
                self.write('    </tr>')
            day = self.first_table_day + datetime.timedelta(delta)
            prev_datetime = None
            css_classes = ['day-%s' % day.strftime('%w')]
            if day == today:
                css_classes.append('today')
            self.write('<td class="%s">', ' '.join(css_classes))
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
        return self.read()
