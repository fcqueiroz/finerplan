$( document ).ready(function() {

    $( "#transaction-0" ).click(function( event ) {
        $( "#basic" ).css('visibility','visible')
        $( "#new_cat_div" ).css('visibility','visible')
        $( "#earnings_category" ).css('display','block')
        $( "#expenses_category" ).css('display','none')
        $( "#pay_method" ).css('visibility','hidden')
    });
    $( "#transaction-1" ).click(function( event ) {
        $( "#basic" ).css('visibility','visible')
        $( "#new_cat_div" ).css('visibility','hidden')
        $( "#earnings_category" ).css('display','none')
        $( "#expenses_category" ).css('display','none')
        $( "#pay_method" ).css('visibility','hidden')
    });
    $( "#transaction-2" ).click(function( event ) {
        $( "#basic" ).css('visibility','visible')
        $( "#new_cat_div" ).css('visibility','visible')
        $( "#earnings_category" ).css('display','none')
        $( "#expenses_category" ).css('display','block')
        $( "#pay_method" ).css('visibility','visible')
    });
    $( "#pay_method-1" ).click(function( event ) {
        $( "#credit_inst" ).css('visibility','visible')
    });
    $( "#pay_method-0" ).click(function( event ) {
        $( "#credit_inst" ).css('visibility','hidden')
    });
    $( "#pay_method-2" ).click(function( event ) {
        $( "#credit_inst" ).css('visibility','hidden')
    });

    $( "#new_cat_div" ).click(function( event ) {
        if(document.getElementById('new_cat_check').checked) {
            $("#new_category").css('visibility','visible')
            $("#earnings_category").css('visibility','hidden')
            $("#expenses_category").css('visibility','hidden')
        } else {
            $("#new_category").css('visibility','hidden')
            $("#earnings_category").css('visibility','visible')
            $("#expenses_category").css('visibility','visible')
            $("#new_cat").val("");
        }
    });
});
