# -*- coding: utf-8 -*-
# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
import datetime
import icemac.ab.calendar.browser.renderer.table
from .resource import calendar_css


class Calendar(object):
    """Tabular calendar display."""

    def update(self):
        calendar_css.need()
        today = datetime.date.today()
        self.month = datetime.date(today.year, today.month, 1)
        events = []
        self.calendar = icemac.ab.calendar.browser.renderer.table.Table(
            self.month, events)

    def render_calendar(self):
        return self.calendar.render()
