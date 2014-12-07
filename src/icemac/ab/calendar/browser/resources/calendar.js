(function($) {
    $('#calendar #calendar-select-form select').on('change', function() {
        $('#calendar #calendar-select-form #form-buttons-apply').click();
    });
    $('#calendar .body .border').height($('#calendar .body table').height());
})(jQuery);
