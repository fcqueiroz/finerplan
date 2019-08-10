
(function($) {
    "use strict";

    /*================================
    datatable active
    ==================================*/
    if ($('#dataTable').length) {
        $('#dataTable').DataTable({
            responsive: true,
            "order": [[ 0, 'desc' ]]
        });
    }
    if ($('#dataTable2').length) {
        $('#dataTable2').DataTable({
            responsive: true,
            "order": [[ 13, 'asc' ]]
        });
    }
}) (jQuery);