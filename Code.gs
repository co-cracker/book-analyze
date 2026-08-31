// ============================================================
// Gemini relay for the book analysis app.
// Keeps the API key on the Google server so the HTML file can be
// shared with anyone without exposing a key.
//
// Setup:
//   1. Paste your key into GEMINI_API_KEY below (aistudio.google.com/apikey)
//   2. Deploy > New deployment > Web app > Access: Anyone
//   3. Copy the /exec URL into GAS_URL inside book_analysis_app.html
//
// Output limit is 8192 because the lie-hunting step returns 8-10 summary
// sentences plus 3 fully described lies, and the analysis steps now return
// a cell anchor plus multi-paragraph prose. 2000 tokens truncated the JSON.
// ============================================================

var GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE';

// Model fallback order. 2.0-flash first, older flash models as backup
// when Google returns 503 (High demand).
var MODELS = [
  'gemini-2.0-flash',
  'gemini-1.5-flash',
  'gemini-1.5-flash-latest'
];

var MAX_TRIES_PER_MODEL = 3;
var RETRY_WAIT_MS = 2000;

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var text = askGemini(body.system || '', body.user || '');
    return json({ text: text });
  } catch (err) {
    return json({ error: String(err && err.message ? err.message : err) });
  }
}

function doGet() {
  return json({ ok: true, models: MODELS });
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function askGemini(system, user) {
  var payload = {
    systemInstruction: { parts: [{ text: system }] },
    contents: [{ role: 'user', parts: [{ text: user }] }],
    generationConfig: { maxOutputTokens: 8192, temperature: 0.5 }
  };

  var lastError = 'no response';

  for (var m = 0; m < MODELS.length; m++) {
    for (var attempt = 0; attempt < MAX_TRIES_PER_MODEL; attempt++) {
      var url = 'https://generativelanguage.googleapis.com/v1beta/models/' +
                MODELS[m] + ':generateContent?key=' + GEMINI_API_KEY;

      var res = UrlFetchApp.fetch(url, {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify(payload),
        muteHttpExceptions: true
      });

      var code = res.getResponseCode();
      var raw = res.getContentText();

      if (code === 200) {
        var data = JSON.parse(raw);
        var cand = data.candidates && data.candidates[0];
        if (cand && cand.content && cand.content.parts && cand.content.parts[0]) {
          return cand.content.parts[0].text;
        }
        // 200 with no usable candidate: usually a safety block or an empty finish
        lastError = 'empty response (' + (cand ? cand.finishReason : 'no candidate') + ')';
        break; // a different model will not help, move on
      }

      lastError = MODELS[m] + ' returned ' + code + ': ' + raw.slice(0, 200);

      // 503 = overloaded, 429 = rate limited. Both are worth retrying.
      if (code === 503 || code === 429) {
        Utilities.sleep(RETRY_WAIT_MS);
        continue;
      }

      break; // other errors: try the next model
    }
  }

  throw new Error(lastError);
}
