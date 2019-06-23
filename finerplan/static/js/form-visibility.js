/*
 * This script controls how elements appear or disappear in the "Add Transaction" form
 */

function hideWobblyFields() {
  $(".field-wobbly").css('display','none')
};

$(function() {
  $( "#transactionRadios" ).change(function() {
    hideWobblyFields();
    $( ".field-" + $(this).find("input[name='transaction']:checked").val() ).css('display','block');
  });
});