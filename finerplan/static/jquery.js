$( document ).ready(function() {

    $( "#transaction-0" ).click(function( event ) {
        $( "#basic" ).css('visibility','visible')
        $( "#category" ).css('visibility','hidden')
        $( "#pay_method" ).css('visibility','hidden')
    });
    $( "#transaction-1" ).click(function( event ) {
        $( "#basic" ).css('visibility','visible')
        $( "#category" ).css('visibility','hidden')
        $( "#pay_method" ).css('visibility','hidden')
    });
    $( "#transaction-2" ).click(function( event ) {
        $( "#basic" ).css('visibility','visible')
        $( "#category" ).css('visibility','visible')
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
});
