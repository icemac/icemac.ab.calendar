# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .base import Calendar
from ..interfaces import UnknownLanguageError
from icemac.addressbook.browser.base import can_access_uri_part
from icemac.addressbook.i18n import _
import datetime
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import zope.component


SPECIAL_CLASS_MAPPING = {
    True: 'red',
}


def render_event_time(datetime, whole_day, request, no_time=''):
    """Render time of event human readable and localized to locale of user."""
    if whole_day:
        return no_time
    formatter = request.locale.dates.getFormatter(
        'time', 'short')
    time = formatter.format(datetime)
    if request.locale.id.language == 'de':
        time += ' Uhr'
    return time


class TableEvent(icemac.addressbook.browser.base.BaseView):
    """View to render an event in the table."""

    action_class = 'edit'
    _action_url = None
    default_text = _('Edit')  # allow at least to edit the entry

    def time(self):
        zero_width_space = '&#x200b;'  # keep printing uniform
        return render_event_time(
            self.context.datetime, self.context.whole_day, self.request,
            no_time=zero_width_space)

    def dd_class(self):
        return SPECIAL_CLASS_MAPPING.get(self.context.special_event)

    def dt_class(self):
        if self.context.whole_day:
            return 'no-screen'

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
            text = self.default_text
        return text

    def info(self):
        return [{'info': x} for x in self._localized(self.context.getInfo)]

    def action_url(self):
        return self.url(self.context.context)


def get_day_names(request):
    """Return a list of localized week day names starting with Sunday."""
    locale_calendar = request.locale.dates.calendars['gregorian']
    day_names = locale_calendar.getDayNames()
    # Move Sunday to position one
    day_names.insert(0, day_names.pop(-1))
    return day_names


class Table(Calendar):
    """Tabular display of a calendar."""

    grok.name('table')
    render_event_adapter_name = 'table-event'

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
        self.write('<table>')
        self.write('  <thead>')
        self.write('    <tr>')
        for index, day_name in enumerate(get_day_names(self.request)):
            self.write('      <th class="day-%s">%s</th>', index, day_name)
        self.write('    </tr>')
        self.write('  </thead>')

    def render(self):
        calendar = self.request.locale.dates.calendars['gregorian']
        day_names = calendar.getDayAbbreviations()
        # Move Sunday to position one
        day_names.insert(0, day_names.pop(-1))
        self.table_head()
        self.write('  <tbody>')
        today = datetime.date.today()
        events = self.events
        add_event_for_day_url = self.get_add_event_for_day_url()
        for delta in xrange(self.num_of_days):
            if delta % 7 == 0:
                # week start
                self.write('    <tr>')
            day = self.first_table_day + datetime.timedelta(delta)
            day_number = int(day.strftime('%w'))
            css_classes = ['day-{}'.format(day_number)]
            if day == today:
                css_classes.append('today')
            self.write('<td class="%s">', ' '.join(css_classes), newline=False)
            if day in self.month:
                self.write('<span class="weekday no-screen">%s</span>',
                           day_names[day_number])
                if add_event_for_day_url:
                    self.write(
                        '<a class="wrapper" href="%s?date=%s" title="%s">',
                        add_event_for_day_url, day.isoformat(),
                        self.translate(_('Add new event for this day.')))
                else:
                    self.write('<span class="wrapper">')
                self.write('<span class="number">%s</span>', day.day)
                if add_event_for_day_url:
                    self.write('</a>')
                else:
                    self.write('</span>')
                found_events_for_day = False
                for ev in events[:]:
                    if ev.datetime.date() != day:
                        # events are sorted, so we can break on day in future
                        break
                    # remove day from list to print to keep for-loop short
                    events.pop(events.index(ev))
                    if not found_events_for_day:
                        self.write('<dl>')
                        found_events_for_day = True
                    view = zope.component.getMultiAdapter(
                        (ev, self.request),
                        name=self.render_event_adapter_name)
                    self.write(view())
                if found_events_for_day:
                    self.write('</dl>')
            self.write('</td>')
            if (delta + 1) % 7 == 0:
                # week end
                self.write('    </tr>')

        self.write('  </tbody>')
        self.write('</table>')
        return self.read()

    def get_add_event_for_day_url(self):
        """Get the URL to add a new a event for a day.

        Returns None if there should be no add link.
        """
        calendar = icemac.ab.calendar.interfaces.ICalendar(
            icemac.addressbook.interfaces.IAddressBook(None))
        if not can_access_uri_part(calendar, self.request, 'addEvent.html'):
            return None
        return self.url(calendar, 'addEvent.html')
