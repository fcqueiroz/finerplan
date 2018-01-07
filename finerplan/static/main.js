var radios = document.getElementById('trans');

radios.onchange = function() {
    var elem = radios.elements[transaction]
    alert(elem)
}

function doSomething() {
    var elem = document.getElementById("pay_methode")
    var val = getRadioVal(elem, 'pay_method')
    //document.getElementById("console").innerHTML =
    alert(val)
}

function getRadioVal(idsse, name) {
    var val;
    // get list of radio buttons with specified name
    var radios = idsse.elements[name];
    alert(radios)

    // loop through list of radio buttons
    for (var i=0, len=radios.length; i<len; i++) {
        if ( radios[i].checked ) { // radio checked?
            val = radios[i].value; // if so, hold its value in val
            break; // and break out of for loop
        }
    }
    alert(val)
    return val; // return value of checked radio or undefined if none checked
}
