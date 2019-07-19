/*
 * This script updates the select fields from the "Add Transaction" form
 */


$(function() {
  $( "#transactionKind" ).change(function() {
    kind = $(this).find("input[name='transaction']:checked").val();

    fetch('/accounts/' + kind).then(function(response) {
      response.json().then(function(data) {
        console.table(data)
        let account_source_select = document.getElementById('account_source');
        optionHTML = '';
        for (let source of data.sources) {
          optionHTML += '<option value="' + source.id + '">' + source.name + '</option>';
        }
        account_source_select.innerHTML = optionHTML;

        let account_destination_select = document.getElementById('account_destination');
        optionHTML = '';
        for (let destination of data.destinations) {
          optionHTML += '<option value="' + destination.id + '">' + destination.name + '</option>';
        }
        account_destination_select.innerHTML = optionHTML;
      })
    })
  })
});