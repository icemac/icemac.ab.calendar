# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt
import zope.interface
import zope.schema


AUSFALL = 'ausfall'
INTERN = 'intern'


class IEventDescription(zope.interface.Interface):
    """Description of a single event which can be rendered."""

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
