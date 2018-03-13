from __future__ import unicode_literals
from datetime import date  # be able to mock date.today() in tests
from icemac.ab.calendar.browser.interfaces import IEventDescription
from icemac.ab.calendar.browser.renderer.table import get_day_names
from icemac.ab.calendar.browser.renderer.table import render_event_time
from icemac.ab.calendar.browser.resource import eventview
from icemac.ab.calendar.eventview.interfaces import IEventViews
from icemac.addressbook.preferences.utils import get_time_zone_name
import datetime
import icemac.ab.calendar.browser.base
import icemac.ab.calendar.eventview.interfaces
import pytz
import z3c.form.interfaces
import zope.cachedescriptors.property
import zope.component


ONE_DAY = datetime.timedelta(days=1)


class EventList(list):
    """List of events."""

    def pop(self, default=None):
        try:
            return super(EventList, self).pop()
        except IndexError:
            return default


class EventView(icemac.ab.calendar.browser.base.View):
    """Render the views configured as event view configurations."""

    start = None
    end = None
    events = None

    def update(self):
        eventview.need()
        self.widget = zope.component.getMultiAdapter(
            (IEventViews['views'], self.request),
            z3c.form.interfaces.IFieldWidget)
        self.widget.update()
        if 'views' in self.request.form:
            # The used select widget is a multi select (which cannot be
            # changed):
            token = self.widget.value[0]
            event_view_config = self.widget.terms.getValue(token)
        else:
            source = IEventViews['views'].source.factory
            event_view_config = source.getValues()[0]
        self.events = EventList(self._get_events(event_view_config))
        self.events.reverse()

    def close_url(self):
        return self.url(self.context, 'month.html')

    def action(self):
        return self.url(self.context, self.__name__)

    def views(self):
        self.widget.klass = "form-control"
        return self.widget.render()

    @zope.cachedescriptors.property.Lazy
    def month_names(self):
        """Return a list of month names (one based!) in locale of user."""
        locale_calendar = self.request.locale.dates.calendars['gregorian']
        return ['NULL'] + locale_calendar.getMonthNames()

    @zope.cachedescriptors.property.Lazy
    def day_names(self):
        return get_day_names(self.request)

    def events_per_month(self):
        month = {
            'month': '{} {}'.format(
                self.month_names[self.start.month], self.start.year),
            'days': [],
        }
        current_day = self.start
        today = datetime.datetime.combine(date.today(), current_day.timetz())
        current_event = self.events.pop(default=None)
        while current_day <= self.end:
            current_week_day = int(current_day.strftime('%w'))
            add_css_dt = []
            add_css_dd = ''
            if not current_week_day:
                # only add this CSS class on Sunday
                add_css_dt.append(' bg-warning')
                add_css_dd = ' bg-warning'
            if current_day == today:
                add_css_dt.append(' text-success')
            day = {
                'day': '{}, {}.'.format(
                    self.day_names[current_week_day], current_day.day),
                'add_css_dt': ''.join(add_css_dt),
                'add_css_dd': add_css_dd,
                'events': [],
            }
            next_day = current_day + ONE_DAY
            while (current_event is not None
                   and current_event.datetime < next_day):
                ed = IEventDescription(current_event)
                event_data = {
                    'event': icemac.addressbook.interfaces.ITitle(
                        current_event),
                    'url': self.url(current_event),
                    'time': render_event_time(ed, self.request),
                    'data': [],
                }
                day['events'].append(event_data)

                current_event = self.events.pop(default=None)

            month['days'].append(day)
            if next_day.day == 1:
                yield month
                month = {
                    'month': '{} {}'.format(
                        self.month_names[next_day.month], next_day.year),
                    'days': [],
                }
            current_day = next_day
        if month['days']:
            yield month

    def _get_events(self, event_view_config):
        """Get events between `start` and `duration` of EventViewConfig."""
        midnight = datetime.time(0, 0, 0, tzinfo=pytz.UTC)
        today = date.today()
        self.start = datetime.datetime.combine(
            today + datetime.timedelta(days=event_view_config.start),
            midnight)
        self.end = self.start + datetime.timedelta(
            days=event_view_config.duration)
        categories = [x.title for x in event_view_config.categories]
        return self.context.get_events(
            self.start, self.end, get_time_zone_name(), categories)