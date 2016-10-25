function retrieve(id1, id2) {
	var textbox1 = document.getElementById(id1);
	var textbox2 = document.getElementById(id2);

	var firstName = textbox1.value;
	var macAddress = textbox2.value;	
}
function openTab(evt, tabName) {
    // Declare all variables
    var i, tabcontent, tablinks, currenttab;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    // currenttab = document.getElementById(tabName)
    // currenttab.style.display = "block"
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}
function codeAddress() {
			openTab(event, 'Access List')
        }

//populate lists for update
var day = document.getElementById("day");
var hour = document.getElementById("hour");
var minute = document.getElementById("minute");

var days = 28;
var hours = 24;
var minutes = 4;

for (var i = 1; i <= days; i++) {
   var opt = i;
   var el = document.createElement("option");
   el.textContent = opt;
   el.value = opt;
   day.appendChild(el)
}

for (var i = 1; i <= hours; i++) {
   var opt = i;
   var el = document.createElement("option");
   el.textContent = opt;
   el.value = opt;
   hour.appendChild(el)
}

for (var i = 0; i < minutes; i++) {
   var opt = i*15;
   var el = document.createElement("option");
   el.textContent = opt;
   el.value = opt;
   minute.appendChild(el)
}