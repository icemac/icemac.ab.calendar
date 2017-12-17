/*global jQuery, Class */
(function($) {
    "use strict";

    // Auto submit month and year drop downs:
    $('#calendar #calendar-select-form select').on('change', function() {
        $('#calendar #calendar-select-form #form-buttons-apply').click();
    });

    // Change width of drop downs in month select on calendar back to "normal"
    // width:
    $('form#calendar-select-form select.choice-field').select2({
        width: "auto",
    });

    var WidgetToggle = Class.$extend({
        /* Toggle the display of a widget and its label depending on clicks. */

        __init__: function (widget_selector, show_on, hide_on) {
            /* widget_selector ... selector of the widget to be toggled
             * show_on ... trigger `show widget` if checked
             * hide_on ... trigger `hide widget` if checked
             */
            if (!$(widget_selector).length)
                // no-op if widget does not exist on page:
                return;
            var self = this;
            self.widget_selector = widget_selector;
            $(show_on).click(function() {
                self.set_widget_display('show', 'fast');});
            $(hide_on).click(function() {
                self.set_widget_display('hide', 'fast');});
            self.set_if_checked(show_on, 'show');
            self.set_if_checked(hide_on, 'hide');
        },

        set_widget_display: function (status, speed) {
            var self = this;
            $(self.widget_selector)[status](speed);
            $(self.widget_selector).parent().prev()[status](speed);
        },

        set_if_checked: function (selector, status) {
            var self = this;
            if ($(selector).is(':checked')) {
                self.set_widget_display(status);
            }
        }
    });

    // Toggle the display of the time field depending on whole_day_event:
    var time_widget_toggle = new WidgetToggle(
        '#form-widgets-datetime-widgets-time',
        '#form-widgets-datetime-widgets-whole_day_event-1',
        '#form-widgets-datetime-widgets-whole_day_event-0');

    // Make length of border divs equal to center table:
    $(window).resize(function() {
        $('#calendar .body .border').height(
            $('#calendar .body .table').height());
    });
    $(window).trigger('resize'); // Initially adapt size.

    var flip_calendar = function(event) {
        var node = $(event.target);
        $('#form-widgets-calendar_month').val(node.data('month'));
        $('#form-widgets-calendar_year').val(node.data('year'));
        $('#form-widgets-calendar_month').change();
        return false;
    };

    $('#calendar .header a.flip').on('click', flip_calendar);

})(jQuery);
