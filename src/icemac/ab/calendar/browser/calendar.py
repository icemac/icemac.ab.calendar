# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from .renderer.interfaces import UnknownLanguageError
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
import zope.component
import zope.interface


class IMonthSelector(zope.interface.Interface):
    """Select a month for display."""

    month = gocept.month.MonthField(title=_('month for display'))


class SelectorForm(icemac.addressbook.browser.base.BaseForm,
                   z3c.formui.form.EditForm):
    """Form to enter the month which should be displayed in the calendar."""

    fields = z3c.form.field.Fields(IMonthSelector)
    successMessage = _('Month changed.')
    id = 'month-select-form'


class Calendar(icemac.ab.calendar.browser.base.View):
    """Tabular calendar display."""

    zope.interface.implements(IMonthSelector)

    @property
    def month(self):
        """Month which should get displayed."""
        month = self.session.get('selected_month')
        if month is None:
            # Store default value:
            self.month = month = gocept.month.Month.current()
        return month

    @month.setter
    def month(self, value):
        self.session['selected_month'] = value

    def update(self):
        self.form = SelectorForm(self, self.request)
        # Write the value the user entered on `self.month`:
        self.form.update()
        events = [
            icemac.ab.calendar.browser.renderer.interfaces.IEventDescription(x)
            for x in self.context.get_events(self.month)]
        self.renderer = zope.component.getMultiAdapter(
            (self.month, self.request, events),
            icemac.ab.calendar.browser.renderer.interfaces.IRenderer,
            name='table')

    def render_calendar(self):
        return self.renderer()

    def render_form(self):
        return self.form.render()

    def time_zone_name(self):
        """User selected time zone name."""
        return icemac.addressbook.preferences.utils.get_time_zone_name()

    def time_zone_prefs_url(self):
        return self.url(icemac.addressbook.interfaces.IAddressBook(self),
                        '++preferences++/ab.timeZone')


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
