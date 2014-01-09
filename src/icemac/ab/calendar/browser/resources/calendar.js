(function($) {
    $('#calendar #month-select-form select').on('change', function() {
        $('#calendar #month-select-form #form-buttons-apply').click();
    });
})(jQuery);
