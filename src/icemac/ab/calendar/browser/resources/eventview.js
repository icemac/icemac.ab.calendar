$(function () {
    // activate popover on close button
    $('[data-toggle="popover"]').popover();

    // Auto submit event view dropdown
    $('#eventview select#views').on('change', function() {
        $('#eventview form').submit();
    });
});
