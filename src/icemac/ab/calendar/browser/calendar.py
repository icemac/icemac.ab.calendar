# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from .resource import calendar_css
from icemac.addressbook.i18n import _
import datetime
import gocept.month
import grokcore.component as grok
import icemac.ab.calendar.browser.renderer.interfaces
import icemac.ab.calendar.browser.renderer.table
import icemac.ab.calendar.interfaces
import icemac.addressbook.browser.base
import pyphen
import z3c.form.field
import z3c.formui.form
import zope.interface


class IMonthSelector(zope.interface.Interface):
    """Select a month for display."""

    month = gocept.month.MonthField(title=_('month for display'))


class SelectorForm(icemac.addressbook.browser.base.BaseForm,
                   z3c.formui.form.EditForm):
    """Form to enter the month which should be displayed in the calendar."""

    fields = z3c.form.field.Fields(IMonthSelector)
    successMessage = _('Month changed.')


class Calendar(object):
    """Tabular calendar display."""

    zope.interface.implements(IMonthSelector)

    def update(self):
        calendar_css.need()
        # The following assignment only sets the default value,
        # `self.form.update()` writes the value the user entered to
        # `self.month`.
        self.month = gocept.month.Month.current()
        self.form = SelectorForm(self, self.request)
        self.form.update()
        events = [
            icemac.ab.calendar.browser.renderer.interfaces.IEventDescription(x)
            for x in self.context.get_events(self.month)]
        self.calendar = icemac.ab.calendar.browser.renderer.table.Table(
            self.month, events)

    def render_calendar(self):
        return self.calendar.render()

    def render_form(self):
        return self.form.render()


class EventDescription(grok.Adapter):
    """Adapter from Event to EventDescription needed by renderer."""

    grok.context(icemac.ab.calendar.interfaces.IEvent)
    grok.implements(
        icemac.ab.calendar.browser.renderer.interfaces.IEventDescription)


    def __init__(self, event):
        self.kind = event.category
        self.datetime = event.datetime
        self.prio = 0
        self.whole_day = False
        self.special_event = None
        self._text = event.alternative_title

    def getText(self, lang='en'):
        text = u''
        if self._text:
            text = self._text
        elif self.kind:
            text = self.kind.title
        dic = pyphen.Pyphen(lang=lang)
        return ' '.join([dic.inserted(word, '&shy;')
                         for word in text.split()])
