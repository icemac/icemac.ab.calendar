from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.ab.calendar.interfaces
import icemac.ab.calendar.masterdata.breadcrumb
import icemac.addressbook.browser.base
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.datamanager
import icemac.addressbook.browser.metadata
import icemac.addressbook.metadata.interfaces
import z3c.form.field
import zope.dublincore.interfaces
import zope.schema.interfaces


class MasterData(object):
    """List of master data of the calendar."""


class CalendarMasterDataBreadCrumb(
        icemac.addressbook.browser.breadcrumb.MasterdataChildBreadcrumb):
    """Breadcrumb for calendar master data."""

    grok.adapts(
        MasterData,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Calendar')


class ModifierMetadataGroup(
        icemac.addressbook.browser.metadata.MetadataBaseGroup):
    """Group displaying only meta data information of modifier.

    To be used when creator is empty and creation date is irrelevant.
    """

    fields = z3c.form.field.Fields(
        icemac.addressbook.metadata.interfaces.IEditor).select('modifier')
    fields += z3c.form.field.Fields(
        zope.dublincore.interfaces.IDCTimes).select('modified')


class CalendarView(icemac.addressbook.browser.base.GroupEditForm):
    """Edit the calendar view settings."""

    groups = (ModifierMetadataGroup,)
    interface = icemac.ab.calendar.interfaces.ICalendarDisplaySettings
    next_url = 'parent'


class CalendarEditBreadCrumb(
        icemac.ab.calendar.masterdata.breadcrumb.CalendarMDChildBreadcrumb):
    """Breadcrumb for calendar master data edit view."""

    grok.adapts(
        CalendarView,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _(u'Edit settings')
    target_url = None


class AnnotationField(icemac.addressbook.browser.datamanager.AnnotationField,
                      grok.MultiAdapter):
    """Special AnnotationField for calendar."""

    grok.adapts(icemac.ab.calendar.interfaces.ICalendar,
                zope.schema.interfaces.IField)

    @property
    def no_security_proxy(self):
        interfaces = [x[1] for x in zope.component.getUtilitiesFor(
            icemac.ab.calendar.interfaces.INoSecurityProxyType)]
        return interfaces
