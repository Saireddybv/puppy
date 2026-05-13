from flask import Flask, jsonify, request, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
import pyperclip
import threading
from pynput import keyboard

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clipboard-sync-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
keyboard_listener = None
listening = False
live_text = ""

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Clipboard Sync</title>
  <style>
    body { font-family: sans-serif; padding: 10px; margin: 0; background: #f5f5f5; height: 100vh; display: flex; }
    .container { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); flex: 1; display: flex; flex-direction: column; }
    .buttons-row { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
    button { padding: 8px 14px; font-size: 13px; cursor: pointer; border: none; border-radius: 5px; background: #007AFF; color: white; font-weight: bold; flex: 1; min-width: 120px; }
    button:active { background: #0051D5; }
    .toggle-btn { background: #666; }
    .toggle-btn.active { background: #34C759; }
    textarea { width: 100%; flex: 1; font-size: 16px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; resize: none; }
    #status { color: green; margin-top: 8px; font-weight: bold; font-size: 14px; }
    .error { color: red !important; }
    .warning { color: orange !important; }
    h2 { color: #333; margin: 0 0 5px 0; font-size: 18px; }
    p { color: #666; margin: 0 0 10px 0; font-size: 12px; }
    .mode-label { font-size: 11px; color: #999; margin-top: 5px; }
  </style>
</head>
<body>
  <div class="container">
    <h2>📋 Clipboard Sync</h2>
    <p>Copy on Windows → Fetch on iPhone/Android | Live Type Anywhere</p>
    <div class="buttons-row">
      <button onclick="fetchClip()">⬇️ Get from PC</button>
      <button onclick="copyToPhone()">📲 Copy to Android</button>
      <button class="toggle-btn" id="toggleBtn" onclick="toggleLiveCapture()">⌨️ Live OFF</button>
    </div>
    <textarea id="box" placeholder="Clipboard content appears here... or live typing will appear here when enabled"></textarea>
    <div id="status"></div>
    <div class="mode-label" id="modeLabel"></div>
  </div>

  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <script>
    let socket = null;
    let isLiveCapturing = false;

    function initWebSocket() {
      socket = io();
      socket.on('connect', () => {
        console.log('Connected to server');
      });
      socket.on('keystroke', (data) => {
        document.getElementById('box').value += data.key;
        const textarea = document.getElementById('box');
        textarea.scrollTop = textarea.scrollHeight;
      });
      socket.on('live_status', (data) => {
        document.getElementById('modeLabel').innerText = '🔴 Live: ' + data.status;
      });
    }

    function fetchClip() {
      document.getElementById('status').innerText = '⏳ Fetching...';
      fetch('/get').then(r => r.json()).then(d => {
        document.getElementById('box').value = d.text;
        document.getElementById('status').innerText = '✅ Fetched from PC!';
        document.getElementById('modeLabel').innerText = '';
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

    function toggleLiveCapture() {
      isLiveCapturing = !isLiveCapturing;
      const btn = document.getElementById('toggleBtn');
      const textarea = document.getElementById('box');
      
      if (isLiveCapturing) {
        btn.innerText = '⌨️ Live ON';
        btn.classList.add('active');
        textarea.value = '';
        textarea.placeholder = '🔴 LIVE: Typing anywhere on PC will appear here...';
        document.getElementById('status').innerText = '🔴 Live capture ENABLED - type anywhere on your PC!';
        document.getElementById('status').classList.remove('error');
        socket.emit('start_capture');
      } else {
        btn.innerText = '⌨️ Live OFF';
        btn.classList.remove('active');
        textarea.placeholder = 'Clipboard content appears here... or live typing will appear here when enabled';
        document.getElementById('status').innerText = '⚪ Live capture disabled';
        document.getElementById('modeLabel').innerText = '';
        socket.emit('stop_capture');
      }
    }

    // Auto-fetch on load
    window.addEventListener('load', () => {
      initWebSocket();
      fetchClip();
    });
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

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print(f'Client connected')
    emit('live_status', {'status': 'listening' if listening else 'stopped'})

@socketio.on('start_capture')
def handle_start_capture():
    global listening, keyboard_listener
    if not listening:
        listening = True
        print('Starting keyboard capture...')
        start_keyboard_listener()
        emit('live_status', {'status': 'capturing keystrokes'}, to=None)

@socketio.on('stop_capture')
def handle_stop_capture():
    global listening, keyboard_listener
    if listening:
        listening = False
        print('Stopping keyboard capture...')
        if keyboard_listener:
            keyboard_listener.stop()
            keyboard_listener = None
        emit('live_status', {'status': 'stopped'}, to=None)

def on_press(key):
    try:
        # Handle regular characters
        if hasattr(key, 'char') and key.char:
            char = key.char
        else:
            # Handle special keys
            special_keys = {
                'space': ' ',
                'enter': '\n',
                'tab': '\t',
                'backspace': '\b',
            }
            key_name = str(key).replace("Key.", "").lower()
            char = special_keys.get(key_name, '')
        
        if char and listening:
            socketio.emit('keystroke', {'key': char}, to=None)
    except Exception as e:
        print(f"Error capturing key: {e}")

def start_keyboard_listener():
    global keyboard_listener
    try:
        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()
        print("Keyboard listener started successfully")
    except Exception as e:
        print(f"Failed to start keyboard listener: {e}")
        global listening
        listening = False

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5055, debug=False)
