from flask import Flask, jsonify, request, render_template_string
import pyperclip

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Clipboard Sync</title>
  <style>
    body { font-family: sans-serif; padding: 20px; max-width: 600px; margin: auto; background: #f5f5f5; }
    .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    textarea { width: 100%; height: 200px; font-size: 16px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
    button { padding: 14px 24px; font-size: 16px; margin: 8px 4px; cursor: pointer; border: none; border-radius: 5px; background: #007AFF; color: white; font-weight: bold; }
    button:active { background: #0051D5; }
    #status { color: green; margin-top: 10px; font-weight: bold; }
    .error { color: red !important; }
    h2 { color: #333; margin-top: 0; }
  </style>
</head>
<body>
  <div class="container">
    <h2>📋 Clipboard Sync</h2>
    <p style="color: #666;">Copy on Windows → Fetch on iPhone/Android</p>
    <button onclick="fetchClip()">⬇️ Get from PC</button>
    <button onclick="copyToPhone()">📲 Copy to Phone</button>
    <br><br>
    <textarea id="box" placeholder="Clipboard content appears here..."></textarea>
    <div id="status"></div>
  </div>

  <script>
    function fetchClip() {
      document.getElementById('status').innerText = '⏳ Fetching...';
      fetch('/get').then(r => r.json()).then(d => {
        document.getElementById('box').value = d.text;
        document.getElementById('status').innerText = '✅ Fetched from PC!';
      }).catch(e => {
        document.getElementById('status').innerText = '❌ Connection error';
        document.getElementById('status').classList.add('error');
      });
    }
    function copyToPhone() {
      const text = document.getElementById('box').value;
      if (!text) {
        document.getElementById('status').innerText = '❌ No text to copy';
        document.getElementById('status').classList.add('error');
        return;
      }
      navigator.clipboard.writeText(text).then(() => {
        document.getElementById('status').innerText = '✅ Copied to phone clipboard!';
        document.getElementById('status').classList.remove('error');
      }).catch(() => {
        document.getElementById('status').innerText = '❌ Copy failed - use manual select & copy';
        document.getElementById('status').classList.add('error');
      });
    }
    // Auto-fetch on load
    fetchClip();
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/get')
def get_clip():
    try:
        text = pyperclip.paste()
    except:
        text = ""
    return jsonify({"text": text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5055, debug=False)
