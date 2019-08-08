/*
 * This script controls fields and data visibility on "Add Report" form
 */

$(function() {
  let genres = ['Information', 'Table', 'Graph']

  /* Makes every field of reports list not required until a genre is chosen */
  for (let genre of genres) {
      let element = document.getElementById(genre + 'Reports')
      element.querySelector('select').required = false;
    }

  $( "#CardType" ).change(function() {
    /* Hides the element that is currently visible and makes it not required */
    for (let genre of genres) {
      let element = document.getElementById(genre + 'Reports')
      if ( ! element.classList.contains('d-none') ) {
        element.classList.add('d-none');
        element.querySelector('select').required = false;
        break;
      }
    }

    /* Makes the right element visible and required */
    let new_genre = $(this).find("#genre option:selected").val()
    if ( genres.includes(new_genre) ) {
      let element_id = new_genre + 'Reports'
      let element = document.getElementById( element_id )
      element.classList.remove('d-none')
      element.querySelector('select').required = true;
    }

  })

});