# Copyright (c) 2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.browser.resource import base_css
import fanstatic
import os.path


# CSS
css_lib = fanstatic.Library('calendar_css', 'resources')


calendar_css = fanstatic.Resource(css_lib, 'calendar.css', depends=[base_css])
