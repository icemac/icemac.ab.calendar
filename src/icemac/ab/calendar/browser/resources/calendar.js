(function($) {
    // Auto submit month and year drop downs:
    $('#calendar #calendar-select-form select').on('change', function() {
        $('#calendar #calendar-select-form #form-buttons-apply').click();
    });
    // Make length of border divs equal to center table:
    $(window).resize(function() {
        $('#calendar .body .border').height(
            $('#calendar .body .table').height());
    });
    $(window).trigger('resize'); // Initially adapt size.
})(jQuery);
