# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt
import zope.interface
import zope.schema


AUSFALL = 'ausfall'
INTERN = 'intern'


class IRenderer(zope.interface.Interface):
    """Renderer for a specific calendar view."""

    def __call__():
        """Return the rendered calendar."""


class IEventDescription(zope.interface.Interface):
    """Description of a single event which can be rendered."""

    context = zope.interface.Attribute('IEvent this description is based on.')

    kind = zope.interface.Attribute('event kind')
    datetime = zope.interface.Attribute('datetime.datetime object')
    prio = zope.interface.Attribute(
        'Event descriptions for the same `datetime` and `kind` with a higher '
        '`prio` override the ones with lower `prio`.')

    whole_day = zope.interface.Attribute(
        'Event is the whole day, so do not display time.')
    special_event = zope.interface.Attribute(
        'One of [AUSFALL, INTERN, None].')

    def getText(lang='en'):
        """Textual description of the event, hyphenated for HTML."""
