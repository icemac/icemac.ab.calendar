# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from .renderer.interfaces import UnknownLanguageError
from .resource import calendar_css
from icemac.addressbook.i18n import _
import copy
import datetime
import decorator
import gocept.month
import grokcore.component as grok
import icemac.ab.calendar.browser.renderer.interfaces
import icemac.ab.calendar.browser.renderer.table
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
import zope.preference.interfaces
import zope.schema.interfaces


class IMonthSelector(zope.interface.Interface):
    """Select a month for display."""

    month = gocept.month.MonthField(title=_('month for display'))


class SelectorForm(icemac.addressbook.browser.base.BaseForm,
                   z3c.formui.form.EditForm):
    """Form to enter the month which should be displayed in the calendar."""

    fields = z3c.form.field.Fields(IMonthSelector)
    successMessage = _('Month changed.')


class Calendar(icemac.addressbook.browser.base.BaseView):
    """Tabular calendar display."""

    zope.interface.implements(IMonthSelector)

    def update(self):
        calendar_css.need()
        # The following assignment only sets the default value,
        # `self.form.update()` writes the value the user entered on
        # `self.month`.
        self.month = gocept.month.Month.current()
        self.form = SelectorForm(self, self.request)
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

@decorator.decorator
def hyphenated(func, context, lang=None):
    """Decorator for methods those return value should be hyphenated.

    Usage:

    @hyphenated
    def method(self, lang=None):
        return text

    Call it using: self.method(lang='de')

    """
    if lang is not None:
        try:
            dic = pyphen.Pyphen(lang=lang)
        except KeyError:
            # Fail early if we cannot hythen the desired language:
            raise UnknownLanguageError()
    text = func(context)
    if lang is not None:
        text = ' '.join([dic.inserted(word, '&shy;')
                         for word in text.split()])
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
            schema_field = icemac.addressbook.entities.get_bound_schema_field(
                self.context,
                icemac.addressbook.interfaces.IEntity(field.interface),
                field)
            info.append(unicode(schema_field.get(schema_field.context)))
        return u', '.join(info)
