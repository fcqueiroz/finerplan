/*
 * This script controls fields and data visibility on "Add Report" form
 */

$(function() {
  let groups = ['Information', 'Table', 'Graph']

  /* Makes every field of reports list not required until a group is chosen */
  for (let group of groups) {
      let element = document.getElementById(group + 'Reports')
      element.querySelector('select').required = false;
    }

  function updatesReportsArea () {
    /* Hides the element that is currently visible and makes it not required */
    for (let group of groups) {
      let element = document.getElementById(group + 'Reports')
      if ( ! element.classList.contains('d-none') ) {
        element.classList.add('d-none');
        element.querySelector('select').required = false;
        break;
      }
    }

    /* Makes the right element visible and required */
    let new_group = $("#group option:selected").val()
    if ( typeof new_group === 'undefined' ) {
      new_group = $( '#group' ).val()
    }
    if ( groups.includes(new_group) ) {
      let element_id = new_group + 'Reports'
      let element = document.getElementById( element_id )
      element.classList.remove('d-none')
      element.querySelector('select').required = true;
    }
  }

  updatesReportsArea()
  $( "#CardType" ).change(updatesReportsArea)

});