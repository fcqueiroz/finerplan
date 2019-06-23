/*
 * This script controls how elements appear or disappear in the "Add Transaction" form
 */

function hideWobblyFields() {
  $(".field-wobbly").css('display','none')
};

var transactionKind

// Changes form's fields based on transaction kind
$(function() {
  $( "#transactionRadios" ).change(function() {
    hideWobblyFields();
    transactionKind = $(this).find("input[name='transaction']:checked").val();
    $( ".field-" + transactionKind ).css('display','block');
    $("#newCategoryCheck").prop('checked', false);
  });
});

// Switches 'category' dropdown selector by 'new category' text field based on checkbox
$(function() {
  $( "#newCategoryCheck" ).change(function() {
    if($(this).is(":checked")) {
      $(".field-new-category").css('display','block');
      $(".field-category").filter(".field-" + transactionKind).css('display','none');
    } else {
      $(".field-new-category").css('display','none')
      $(".field-category").filter(".field-" + transactionKind).css('display','block');
      $("#new_cat").val("");
    }
  });
});