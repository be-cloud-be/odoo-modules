// The Browser API key obtained from the Google Developers Console.
var developerKey = 'xxxxxxxYYYYYYYY-12345678';

// The Client ID obtained from the Google Developers Console. Replace with your own Client ID.
var clientId = "1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com"

// Scope to use to access user's photos.
var scope = ['https://www.googleapis.com/auth/photos'];

var pickerApiLoaded = false;
var oauthToken;

function onAuthApiLoad() {
  window.gapi.auth.authorize(
      {
        'client_id': clientId,
        'scope': scope,
        'immediate': false
      },
      handleAuthResult);
}

function onPickerApiLoad() {
  pickerApiLoaded = true;
  createPicker();
}

function handleAuthResult(authResult) {
  if (authResult && !authResult.error) {
    oauthToken = authResult.access_token;
  }
}

//Use the API Loader script to load google.picker and gapi.auth.
gapi.load('auth', {'callback': onAuthApiLoad});
gapi.load('picker', {'callback': onPickerApiLoad});
