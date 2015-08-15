// The Client ID of Imply.lu
var clientId = "433547367780-b8758n8k6ridvai3tcf31dfnic438h5e.apps.googleusercontent.com"

var scope = ['https://www.googleapis.com/auth/drive'];

var pickerApiLoaded = false;
var oauthToken = false;

// Use the API Loader script to load google.picker and gapi.auth.
function onApiLoad() {
  gapi.load('auth', {'callback': onAuthApiLoad});
  gapi.load('picker', {'callback': onPickerApiLoad});
}

function onAuthApiLoad() {
  window.gapi.auth.authorize(
      {
        'client_id': clientId,
        'scope': scope,
        'immediate': false,
        'include_granted_scopes' : true
      },
      handleAuthResult);
}

function onPickerApiLoad() {
  pickerApiLoaded = true;
}

function handleAuthResult(authResult) {
  if (authResult && !authResult.error) {
    oauthToken = authResult.access_token;
  } else {
	alert("Cannot get authorization token for Google Drive: " + authResult.error_subtype + " - " + authResult.error);
  }
}