/*
 * This script controls fields and data visibility on "Add Transaction" form
 */

function updateAccounts(id, data) {
  let account_select = document.getElementById(id);
  optionHTML = '';
  regex = /(Expenses - )|(Income - )/g;
  for (let account of data) {
    optionHTML += '<option value="' + account.id + '">' + account.name.replace(regex, '') + '</option>';
  }
  account_select.innerHTML = optionHTML;
}

function saveIdsThatDisplayInstallments(data) {
  var installments_ids = []
  sources = data.source
  for (let account of data) {
    if (account.type == 'credit_card') {
      installments_ids.push(account.id)
    }
  }
  sessionStorage.installments_ids = installments_ids
}

$(function() {
  /* updates the account select fields based on transaction kind */
  $( "#transactionKind" ).change(function() {
    kind = $(this).find("input[name='transaction_kind']:checked").val();

    fetch('/accounts/' + kind).then(function(response) {
      response.json().then(function(data) {
        saveIdsThatDisplayInstallments(data.sources)

        updateAccounts('source_id', data.sources)
        updateAccounts('destination_id', data.destinations)
      })
    })
    document.getElementById('AccountsArea').classList.remove('d-none');
  })

  /* displays or hides InstallmentsArea based on source account chosen */
  $( "#source_id" ).change(function() {
    installments_ids = sessionStorage.installments_ids
    if ( installments_ids.includes($(this).val()) ) {
      document.getElementById('InstallmentsArea').classList.remove('d-none');
    } else {
      document.getElementById('InstallmentsArea').classList.add('d-none');
    }
  })

});