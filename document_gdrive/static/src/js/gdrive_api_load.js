// The Client ID of Imply.lu
//var clientId = "433547367780-r5c3iju0u3q2fv2ae5kfld76hi0i1o5c.apps.googleusercontent.com"

//var scope = ['https://www.googleapis.com/auth/drive'];

var pickerApiLoaded = false;
//var oauthToken;

// Use the API Loader script to load google.picker and gapi.auth.
function onApiLoad() {
  /*gapi.load('auth', {'callback': onAuthApiLoad});*/
  gapi.load('picker', {'callback': onPickerApiLoad});
}

function onAuthApiLoad() {
  /*window.gapi.auth.authorize(
      {
        'client_id': clientId,
        'scope': scope,
        'immediate': true
      },
      handleAuthResult);*/
}

function onPickerApiLoad() {
  pickerApiLoaded = true;
}

/*function handleAuthResult(authResult) {
  if (authResult && !authResult.error) {
    oauthToken = authResult.access_token;
  } else {
	alert("Cannot get authorization token for Google Drive: " + authResult.error_subtype + " - " + authResult.error);
  }
}*/