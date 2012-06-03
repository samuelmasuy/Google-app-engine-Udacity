window.onload = initPage;

function initPage() {
	var usr1 = document.getElementById("usr1");
	var usr2 = document.getElementById("usr2");
	var register = document.getElementById("register");
	var pass1 = document.getElementById("pass1");
	var pass2  = document.getElementById("pass2");
	var verify1 = document.getElementById("verify1");
	var verify2 = document.getElementById("verify2");
	var email1 = document.getElementById("email1");
	var email2 = document.getElementById("email2");
  usr2.onblur = checkUsername;
  register.disabled = true;
}
function checkUsername() {
	// request = createRequest();
	if (window.XMLHttpRequest)
	{// code for IE7+, Firefox, Chrome, Opera, Safari
		request = new XMLHttpRequest();
	}
	else
	{// code for IE6, IE5
		request = new ActiveXObject("Microsoft.XMLHTTP");
	}
	if (request == null) {
		alert("Unable to create request");
	} else {
		var theName = usr2.value
		var username = escape(theName);
		var url = "checkuser?username=" + username;
		request.onreadystatechange = showUsernameStatus;
		request.open("GET", url, true);
		request.send(null);
	}
}
function showUsernameStatus() {
	if (request.readyState == 4) {
		if (request.status == 200) {
			if (request.responseText == "notgood"){
				// if there's a problem, we'll tell the user
				usr1.innerHTML = "That user already exists.";
				usr2.style.boxShadow="0 0 5px rgba(255,0,0,0.4)";
    		usr2.style.border="1px solid rgba(255,0,0,0.4)"; 
				register.disabled = true;
			}
			else {
				// if it's okay, no error message to show
				register.disabled = false;
				usr2.style.border="";
    		usr2.style.boxShadow="";
			}
		}
	}
}
function check_username () {
  var re = /[^A-Za-z0-9'\.&@:?!()$#^]/
  value = usr2.value
  if (re.test(value)) {
    usr1.innerHTML = "Not a valid username.";
    usr2.style.boxShadow="0 0 5px rgba(255,0,0,0.4)";
    usr2.style.border="1px solid rgba(255,0,0,0.4)";   
    register.disabled = true;
  }
  else if (value.length >20 || value.length <3) {
    usr1.innerHTML = "3-20 characters.";
    usr2.style.boxShadow="0 0 5px rgba(255,0,0,0.4)";
    usr2.style.border="1px solid rgba(255,0,0,0.4)";
    register.disabled = true;
  }
  else {
    usr1.innerHTML = "";
    usr2.style.border="";
    usr2.style.boxShadow="";
    register.disabled = false;
  }
}
function check_pass() {
  var re = /[^A-Za-z0-9'\.&@:?!()$#^]/
  value = pass2.value
  if (re.test(value)) {
    pass1.innerHTML = "Not a valid password.";
    pass2.style.boxShadow="0 0 5px rgba(255,0,0,0.4)";
    pass2.style.border="1px solid rgba(255,0,0,0.4)";  
    register.disabled = true;
  }
  else if (value.length >20 || value.length <3) {
    pass1.innerHTML = "3-20 characters.";
    pass2.style.boxShadow="0 0 5px rgba(255,0,0,0.4)";
    pass2.style.border="1px solid rgba(255,0,0,0.4)";  
    register.disabled = true;
  }
  else {
    pass1.innerHTML = "";
    pass2.style.boxShadow="";
    pass2.style.border="";  
    register.disabled = false;
  }
}
function check_verify() {
  word = pass2.value;
  value = value = verify2.value
  if (value == word || !value) {
    verify1.innerHTML = "";
    verify2.style.boxShadow="";
    verify2.style.border="";  
    register.disabled = false;
  }
  else {
    verify1.innerHTML = "Passwords do not match.";
    verify2.style.boxShadow="0 0 5px rgba(255,0,0,0.4)";
    verify2.style.border="1px solid rgba(255,0,0,0.4)";  
    register.disabled = true;
  }
}
function check_email() {
  value = email2.value
  var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  if (re.test(value) || !value ) {
    email1.innerHTML = "";
    email2.style.boxShadow="";
    email2.style.border="";  
    register.disabled = false;
  }
  else {
    email1.innerHTML = "Not a valid email.";
    email2.style.boxShadow="0 0 5px rgba(255,0,0,0.4)";
    email2.style.border="1px solid rgba(255,0,0,0.4)"; 
    register.disabled = true;
  }
}