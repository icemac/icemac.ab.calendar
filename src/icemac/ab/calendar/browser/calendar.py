# -*- coding: utf-8 -*-
from .interfaces import IEventDescription
from .interfaces import UnknownLanguageError
from datetime import date
from icemac.addressbook.i18n import _
import cgi
import collections
import copy
import decorator
import gocept.month
import grokcore.component as grok
import icemac.ab.calendar.browser.base
import icemac.ab.calendar.browser.renderer.interfaces
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.interfaces
import icemac.addressbook.preferences.utils
import pyphen
import pytz
import z3c.form.field
import z3c.formui.form
import zc.sourcefactory.basic
import zope.cachedescriptors.property
import zope.component
import zope.globalrequest
import zope.interface


class Dispatcher(icemac.ab.calendar.browser.base.View):
    """Dispatch to month resp. year view."""

    possible_views = collections.defaultdict(
        lambda: 'month.html', {
            'year': 'year.html',
            'event-view': 'event-view.html',
        })
    known_targets = tuple(possible_views.keys()) + ('month',)

    def __call__(self):
        target = self.request.get('to', None)
        if target in self.known_targets:
            self.session['calendar_view'] = target
        else:
            target = self.session.get('calendar_view', 'month')
        self.request.response.redirect(
            self.url(self.context, self.possible_views[target]))
        return ''


class MonthSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Enumerates months."""

    def getValues(self):
        return range(1, 13)

    def getTitle(self, value):
        request = zope.globalrequest.getRequest()
        calendar = request.locale.dates.calendars['gregorian']
        return calendar.months.get(value)[0]


month_source = MonthSource()


class YearSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Enumerate 5 years past + 10 years future."""

    def getValues(self):
        current_year = date.today().year
        return range(current_year - 5, current_year + 11)


year_source = YearSource()


class IMonthSelector(zope.interface.Interface):
    """Select a month for display."""

    calendar_month = zope.schema.Choice(title=_('month'), source=month_source)
    calendar_year = zope.schema.Choice(title=_('year'), source=year_source)


class MonthSelectorForm(icemac.addressbook.browser.base.BaseForm,
                        z3c.formui.form.EditForm):
    """Form to enter the month which should be displayed in the calendar."""

    fields = z3c.form.field.Fields(IMonthSelector)
    successMessage = _('Month changed.')
    id = 'calendar-select-form'


class TabularCalendar(icemac.ab.calendar.browser.base.View):
    """Tabular calendar display."""

    form_class = NotImplemented
    css_class = NotImplemented
    month_names = None  # set in `update()`

    @property
    def calendar_year(self):
        year = self.session.get('calendar_year')
        if year is None:
            # Store default value:
            self.calendar_year = year = gocept.month.Month.current().year
        return year

    @calendar_year.setter
    def calendar_year(self, value):
        self.session['calendar_year'] = value

    def selected_css_class(self, name):
        calendar_view = self.session.get('calendar_view')
        if calendar_view == name:
            return 'selected'
        # no selection in session, use default:
        if calendar_view is None and name == 'month':
            return 'selected'

    def menu_url(self, target):
        return self.url(self.context, to=target)

    def update(self):
        locale_calendar = self.request.locale.dates.calendars['gregorian']
        self.month_names = locale_calendar.getMonthNames()
        self.update_form()

    def update_form(self):
        self.form = self.form_class(self, self.request)
        # Write the value the user entered on self:
        self.form.update()

    def render_form(self):
        return self.form.render()

    def time_zone_name(self):
        """User selected time zone name."""
        return icemac.addressbook.preferences.utils.get_time_zone_name()

    def time_zone_prefs_url(self):
        return self.url(icemac.addressbook.interfaces.IAddressBook(self),
                        '++preferences++/ab.timeZone')

    def get_month_name(self, month):
        """Render the month name of a gocept.month instance."""
        return self.month_names[month.month - 1]

    def previous_link(self):
        return ''

    def next_link(self):
        return ''

    def events_in_interval(self, start, end, condition=lambda x: True):
        """Get all events in an interval filtered by a condition function.

        Returns list of tuples (month, [event-description, event-description]).
        """
        year = gocept.month.MonthInterval(start, end)
        return [(
            month,
            [IEventDescription(x)
             for x in self.context.get_events_for_month(
                month, self.time_zone_name())
             if condition(x)]
        ) for month in year]


@zope.interface.implementer(IMonthSelector)
class MonthCalendar(TabularCalendar):
    """Calendar display of one month."""

    form_class = MonthSelectorForm
    css_class = 'month'
    renderer_name = 'table'
    title = _('Month tabular view')

    @property
    def calendar_month(self):
        month = self.session.get('calendar_month')
        if month is None:
            # Store default value:
            self.calendar_month = month = gocept.month.Month.current().month
        return month

    @calendar_month.setter
    def calendar_month(self, value):
        self.session['calendar_month'] = value

    @zope.cachedescriptors.property.Lazy
    def month(self):
        """Month which should get displayed."""
        return gocept.month.Month(self.calendar_month, self.calendar_year)

    def update(self):
        super(MonthCalendar, self).update()
        self.renderer = zope.component.getMultiAdapter(
            (self.month, self.request, self.get_event_descriptions()),
            icemac.ab.calendar.browser.renderer.interfaces.IRenderer,
            name=self.renderer_name)

    def previous_link(self):
        prev_month = self.month - 1
        url = '#month={0.month}&year={0.year}'.format(prev_month)
        return {'url': url,
                'month': prev_month.month,
                'year': prev_month.year,
                'text': u'◄'}

    def next_link(self):
        next_month = self.month + 1
        url = '#month={0.month}&year={0.year}'.format(next_month)
        return {'url': url,
                'month': next_month.month,
                'year': next_month.year,
                'text': u'►'}

    def get_event_descriptions(self):
        return [IEventDescription(x)
                for x in self.context.get_events_for_month(
                    self.month, self.time_zone_name())]

    def render_calendar(self):
        return u'<h2 class="no-screen">{month} {year}</h2>\n{cal}'.format(
            month=self.get_month_name(self.month), year=self.month.year,
            cal=self.renderer())


class IYearSelector(zope.interface.Interface):
    """Select a month for display."""

    calendar_year = zope.schema.Choice(title=_('year'), source=year_source)


class YearSelectorForm(icemac.addressbook.browser.base.BaseForm,
                       z3c.formui.form.EditForm):
    """Form to enter the year which should be displayed in the calendar."""

    fields = z3c.form.field.Fields(IYearSelector)
    successMessage = _('Year changed.')
    id = 'calendar-select-form'


@zope.interface.implementer(IYearSelector)
class YearCalendar(TabularCalendar):
    """Calendar displaying a whole year."""

    form_class = YearSelectorForm
    css_class = 'year'
    title = _('Year tabular view')

    def update(self):
        super(YearCalendar, self).update()
        self.events = self.events_in_interval(
            gocept.month.Month(1, self.calendar_year),
            gocept.month.Month(12, self.calendar_year))

    def render_events(self, month, events):
        prefix = u'<div class="month">\n<h2>{} {}</h2>'.format(
            self.get_month_name(month), month.year)
        suffix = u'</div>'
        calendar = zope.component.getMultiAdapter(
            (month, self.request, events),
            icemac.ab.calendar.browser.renderer.interfaces.IRenderer,
            name='table')()
        return '\n'.join((prefix, calendar, suffix))

    def render_calendar(self):
        result = [self.render_events(month, events)
                  for month, events in self.events]
        return '\n'.join(result)


SOFT_HYPHEN = u'\u00AD'
SOFT_HYPHEN_HTML = u'&shy;'


def hyphenate(text, dic):
    """Hyphenate a `text` using `dic`tionary for display in browser."""
    # HTML escape needs to be done *after* the hyphenation, otherwise the
    # entities are hyphenated. Thus there is a two step process:
    # 1. Hyphenate with a special marker
    # 2. replace marker with the actual entity
    if dic is None:
        hyphenated = text
    else:
        words = text.split(u' ')
        hyphenated = u' '.join(
            [dic.inserted(word, SOFT_HYPHEN) for word in words])
    escaped = cgi.escape(hyphenated)
    return escaped.replace(SOFT_HYPHEN, SOFT_HYPHEN_HTML)


@decorator.decorator
def hyphenated(func, context, lang=None):
    """Decorator for methods those return value should be hyphenated.

    Usage:

    @hyphenated
    def method(self, lang=None):
        return text

    Call it using: self.method(lang='de')

    """
    if lang is None:
        dic = None
    else:
        try:
            dic = pyphen.Pyphen(lang=lang)
        except KeyError:
            # Fail early if we cannot hyphen the desired language:
            raise UnknownLanguageError()
    text = func(context)
    if isinstance(text, list):
        text = [hyphenate(x, dic) for x in text]
    else:
        text = hyphenate(text, dic)
    return text


class EventDescriptionBase(object):
    """Base class for event adapters."""

    def __init__(self, context):
        self.context = context
        timezone = pytz.timezone(
            icemac.addressbook.preferences.utils.get_time_zone_name())
        if context.datetime is None:
            self.datetime = None
        else:
            self.datetime = context.in_timezone(timezone)
        self.whole_day = context.whole_day_event
        self._text = icemac.addressbook.interfaces.ITitle(context)
        self.persons = u', '.join(context.listPersons())

    def _get_info_from_fields(self, fields):
        """Convert a list of entitiy fields to a list of data."""
        info = []
        for field in fields:
            if field is icemac.ab.calendar.interfaces.IEvent['persons']:
                value = self.persons
            else:
                schema_field = (
                    icemac.addressbook.entities.get_bound_schema_field(
                        self.context, None, field,
                        default_attrib_fallback=False))
                try:
                    value = schema_field.get(schema_field.context)
                except AttributeError:
                    # Field defined on IEvent but not on IRecurringEvent, thus
                    # it does not exist on the RecurredEvent.
                    value = None
                if value is not None:
                    value = unicode(value)
            if value:
                if field is icemac.ab.calendar.interfaces.IEvent['text']:
                    info.extend(value.split('\n'))
                else:
                    info.append(value)
        return info


class EventDescription(EventDescriptionBase, grok.Adapter):
    """Adapter from IEvent to IEventDescription needed by renderer."""

    grok.context(icemac.ab.calendar.interfaces.IBaseEvent)
    grok.implements(IEventDescription)

    def __init__(self, context):
        super(EventDescription, self).__init__(context)
        self.prio = 0
        self.whole_day = context.whole_day_event
        self.special_event = None
        calendar = icemac.ab.calendar.interfaces.ICalendar(context)
        # Without the following line we get a ForbidenError for
        # `__getitem__` when accessing the annotations where
        # `ICalendarDisplaySettings` are stored. As only authorized users
        # are able to access this adapter, this is no security hole.
        unsave_calendar = zope.security.proxy.getObject(calendar)
        # Making a copy so changing is not possible:
        self._info_fields = copy.copy(
            icemac.ab.calendar.interfaces.ICalendarDisplaySettings(
                unsave_calendar).event_additional_fields)

    @hyphenated
    def getText(self, lang=None):
        return self._text

    @hyphenated
    def getInfo(self, lang=None):
        return self._get_info_from_fields(self._info_fields)


@grok.adapter(IEventDescription)
@grok.implementer(icemac.ab.calendar.interfaces.IEvent)
def event_for_event_description(ed):
    """Get the event an event description was created from."""
    return ed.context


@grok.adapter(IEventDescription)
@grok.implementer(icemac.ab.calendar.interfaces.ICalendar)
def calendar_for_event_description(ed):
    """Get the calendar an event description belongs to."""
    return icemac.ab.calendar.interfaces.ICalendar(ed.context)
