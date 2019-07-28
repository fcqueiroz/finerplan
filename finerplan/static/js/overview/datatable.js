
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
}) (jQuery);