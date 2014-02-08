# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Michael Howitz
# See also LICENSE.txt
from .renderer.interfaces import UnknownLanguageError, IEventDescription
from datetime import date
from icemac.addressbook.i18n import _
import cgi
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
import itertools
import pyphen
import z3c.form.field
import z3c.formui.form
import zc.sourcefactory.basic
import zope.component
import zope.globalrequest
import zope.interface


class Dispatcher(icemac.ab.calendar.browser.base.View):
    """Dispatch to month resp. year view."""

    possible_views = {'month': 'month.html',
                      'year': 'year.html'}

    def __call__(self):
        target = self.request.get('to', None)
        if target in self.possible_views:
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
        return calendar.getMonthNames()[value - 1]

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
        if self.session.get('calendar_view') == name:
            return 'selected'

    def menu_url(self, target):
        return self.url(self.context, to=target)

    def update(self):
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


class MonthCalendar(TabularCalendar):
    """Calendar display of one month."""

    zope.interface.implements(IMonthSelector)
    form_class = MonthSelectorForm
    css_class = 'month'

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

    @property
    def month(self):
        """Month which should get displayed."""
        return gocept.month.Month(self.calendar_month, self.calendar_year)

    def update(self):
        super(MonthCalendar, self).update()
        events = [IEventDescription(x)
                  for x in self.context.get_events(self.month)]
        self.renderer = zope.component.getMultiAdapter(
            (self.month, self.request, events),
            icemac.ab.calendar.browser.renderer.interfaces.IRenderer,
            name='table')

    def render_calendar(self):
        return self.renderer()


class IYearSelector(zope.interface.Interface):
    """Select a month for display."""

    calendar_year = zope.schema.Choice(title=_('year'), source=year_source)


class YearSelectorForm(icemac.addressbook.browser.base.BaseForm,
                       z3c.formui.form.EditForm):
    """Form to enter the year which should be displayed in the calendar."""

    fields = z3c.form.field.Fields(IYearSelector)
    successMessage = _('Year changed.')
    id = 'calendar-select-form'


class YearCalendar(TabularCalendar):
    """Calendar displaying a whole year."""

    zope.interface.implements(IYearSelector)
    form_class = YearSelectorForm
    css_class = 'year'

    def update(self):
        super(YearCalendar, self).update()
        year = gocept.month.MonthInterval(
            gocept.month.Month(1, self.calendar_year),
            gocept.month.Month(12, self.calendar_year))
        self.events = []
        for month in year:
            events = [IEventDescription(x)
                      for x in self.context.get_events(month)]
            self.events.append((month, events))
        locale_calendar = self.request.locale.dates.calendars['gregorian']
        self.month_names = locale_calendar.getMonthNames()

    def render_events(self, month, events):
        month_name = self.month_names[month.month - 1]
        headline = u'<h2>{} {}</h2>'.format(month_name, month.year)
        calendar = zope.component.getMultiAdapter(
            (month, self.request, events),
            icemac.ab.calendar.browser.renderer.interfaces.IRenderer,
            name='table')()
        return '\n'.join((headline, calendar))

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


class EventDescription(grok.Adapter):
    """Adapter from Event to EventDescription needed by renderer."""

    grok.context(icemac.ab.calendar.interfaces.IEvent)
    grok.implements(
        icemac.ab.calendar.browser.renderer.interfaces.IEventDescription)

    def __init__(self, context):
        super(EventDescription, self).__init__(context)
        self.kind = context.category
        self.datetime = context.datetime
        self.prio = 0
        self.whole_day = False
        self.special_event = None
        self._text = context.alternative_title
        self.persons = u', '.join(sorted(itertools.chain(
            [icemac.addressbook.interfaces.IPersonName(x).get_name()
             for x in (context.persons or [])],
            (context.external_persons or []))))
        calendar = icemac.ab.calendar.interfaces.ICalendar(context)
        # Without the following line we get a ForbidenError for
        # `__getitem__` when accessing the annotations where
        # `ICalendarDisplaySettings` are stored. As only authorized users
        # are able to access this adapter, this is no security hole.
        unsave_calendar = zope.security.proxy.getObject(calendar)
        # Making a copy so changing is not possible:
        self.info_fields = copy.copy(
            icemac.ab.calendar.interfaces.ICalendarDisplaySettings(
                unsave_calendar).event_additional_fields)

    @hyphenated
    def getText(self, lang=None):
        text = u''
        if self._text:
            text = self._text
        elif self.kind:
            text = self.kind.title
        return text

    @hyphenated
    def getInfo(self, lang=None):
        info = []
        for field in self.info_fields:
            if field is icemac.ab.calendar.interfaces.IEvent['persons']:
                value = self.persons
            else:
                schema_field = (
                    icemac.addressbook.entities.get_bound_schema_field(
                        self.context,
                        icemac.addressbook.interfaces.IEntity(field.interface),
                        field))
                value = schema_field.get(schema_field.context)
                if value is not None:
                    value = unicode(value)
            if value:
                info.append(value)
        return info
