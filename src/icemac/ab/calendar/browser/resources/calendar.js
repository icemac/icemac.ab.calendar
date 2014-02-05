(function($) {
    $('#calendar #calendar-select-form select').on('change', function() {
        $('#calendar #calendar-select-form #form-buttons-apply').click();
    });
})(jQuery);
