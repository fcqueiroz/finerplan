/*
 * This script controls how elements appear or disappear in the "Add Transaction" form
 */

function hideWobblyFields() {
  $(".field-wobbly").css('display','none')
};

var transactionKind

// Changes form's fields based on transaction kind
$(function() {
  $( "#transactionKind" ).change(function() {
    hideWobblyFields();
    transactionKind = $(this).find("input[name='transaction']:checked").val();
    $( ".field-" + transactionKind ).css('display','flex');

    // Clear some fields values
    $("#newCategoryCheck").prop('checked', false);
    $("#paymentMethod").find("input[name='pay_method']:checked").prop('checked', false);
    $("#paymentInstallments").css('display', 'none');
    $("#paymentInstallments").find("input").val("1");
  });
});

// Switches 'category' dropdown selector by 'new category' text field based on checkbox
$(function() {
  $( "#newCategoryCheck" ).change(function() {
    if($(this).is(":checked")) {
      $(".field-new-category").css('display','flex');
      $(".field-category").filter(".field-" + transactionKind).css('display','none');
    } else {
      $(".field-new-category").css('display','none')
      $(".field-category").filter(".field-" + transactionKind).css('display','flex');
      $("#new_cat").val("");
    }
  });
});

// Toggles 'instalments' fields based on payment method
$(function() {
  $( "#paymentMethod" ).change(function() {
    if( $(this).find("input[name='pay_method']:checked").val() == 'Crédito' ) {
      $("#paymentInstallments").css('display', 'flex');
    } else {
      $("#paymentInstallments").css('display', 'none');
    }
    $("#paymentInstallments").find("input").val("1");  // Resets value
  });
});