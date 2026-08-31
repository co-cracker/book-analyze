// Gemini relay for the book analysis app.
// Only needed when you want to share the HTML file with other people.
// If you use it alone, put the API key straight into the page instead.
//
// Setup
//   1. Paste your key below (get one free at aistudio.google.com/apikey)
//   2. Deploy > New deployment > Web app > Access: Anyone
//   3. Copy the /exec URL into the page's connection panel
//
// Output limit is 8192 because the analysis returns a cell anchor plus
// multi paragraph prose, and the lie hunt returns 8-10 sentences with
// 3 fully described lies. 2000 tokens truncated the JSON mid object.

var GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE';

var MODELS = [
  'gemini-2.0-flash',
  'gemini-1.5-flash',
  'gemini-1.5-flash-latest'
];

function callGemini(systemText, userText) {
  var lastError = '';

  for (var m = 0; m < MODELS.length; m++) {
    var url = 'https://generativelanguage.googleapis.com/v1beta/models/'
      + MODELS[m] + ':generateContent?key=' + GEMINI_API_KEY;

    var requestBody = {
      systemInstruction: { parts: [{ text: systemText }] },
      contents: [{ role: 'user', parts: [{ text: userText }] }],
      generationConfig: { maxOutputTokens: 8192, temperature: 0.5 }
    };

    var options = {
      method: 'post',
      contentType: 'application/json',
      muteHttpExceptions: true,
      payload: JSON.stringify(requestBody)
    };

    // Same model, up to 3 tries. Google returns 503 under load.
    for (var attempt = 0; attempt < 3; attempt++) {
      try {
        var response = UrlFetchApp.fetch(url, options);
        var result = JSON.parse(response.getContentText());

        if (result.error) {
          lastError = result.error.message || JSON.stringify(result.error);
          if (result.error.code === 503 || result.error.status === 'UNAVAILABLE'
              || result.error.code === 429) {
            Utilities.sleep(3000);
            continue;
          }
          break; // other errors: move to the next model
        }

        var text = '';
        if (result.candidates && result.candidates[0] &&
            result.candidates[0].content && result.candidates[0].content.parts) {
          text = result.candidates[0].content.parts[0].text;
        }
        if (text) return { text: text };

        // 200 with no text means a safety block or an empty finish.
        // A different model will not help, so stop here.
        lastError = 'empty response';
        break;

      } catch (err) {
        lastError = err.toString();
        Utilities.sleep(2000);
      }
    }
  }

  return { error: 'all models failed: ' + lastError };
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var result = callGemini(body.system || '', body.user || '');
    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput('OK')
    .setMimeType(ContentService.MimeType.TEXT);
}
