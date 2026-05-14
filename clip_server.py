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
    .main-container { display: flex; gap: 10px; width: 100%; }
    .panel { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); flex: 1; display: flex; flex-direction: column; }
    .buttons-row { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
    button { padding: 8px 12px; font-size: 12px; cursor: pointer; border: none; border-radius: 5px; background: #007AFF; color: white; font-weight: bold; flex: 1; min-width: 70px; white-space: nowrap; }
    button:active { background: #0051D5; }
    .toggle-btn { background: #666; }
    .toggle-btn.active { background: #34C759; }
    textarea { width: 100%; flex: 1; font-size: 16px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; resize: none; font-family: monospace; }
    .status { color: green; margin-top: 8px; font-weight: bold; font-size: 12px; }
    .error { color: red !important; }
    .warning { color: orange !important; }
    .success { color: green !important; }
    h3 { color: #333; margin: 0 0 10px 0; font-size: 16px; border-bottom: 2px solid #007AFF; padding-bottom: 8px; }
    .mode-label { font-size: 11px; color: #999; margin-top: 5px; }
    .panel-divider { width: 1px; background: #ddd; }
    @media (max-width: 768px) { .main-container { flex-direction: column; } }
  </style>
</head>
<body>
  <div class="main-container">
    <!-- Left Panel: Clipboard -->
    <div class="panel">
      <h3>📋 Clipboard from PC</h3>
      <div class="buttons-row">
        <button onclick="fetchClip()">⬇️ Get from PC</button>
        <button onclick="copyToPhone()">📲 Copy</button>
      </div>
      <textarea id="clipboardBox" placeholder="Click 'Get from PC' to fetch clipboard content..."></textarea>
      <div id="clipStatus" class="status"></div>
    </div>

    <!-- Right Panel: Live Typing -->
    <div class="panel">
      <h3>⌨️ Live Typing</h3>
      <div class="buttons-row">
        <button class="toggle-btn" id="toggleBtn" onclick="toggleLiveCapture()">Live ON</button>
        <button onclick="clearLiveBox()">Clear</button>
        <button onclick="copyLiveBox()">Copy</button>
      </div>
      <textarea id="liveBox" placeholder="Enable 'Live' to capture all typing from your PC..."></textarea>
      <div id="liveStatus" class="status"></div>
      <div class="mode-label" id="modeLabel"></div>
    </div>
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
        const liveBox = document.getElementById('liveBox');
        if (data.key === '\b') {
          // Handle backspace - remove last character
          liveBox.value = liveBox.value.slice(0, -1);
        } else {
          liveBox.value += data.key;
        }
        liveBox.scrollTop = liveBox.scrollHeight;
      });
      socket.on('live_status', (data) => {
        document.getElementById('modeLabel').innerText = '🔴 Status: ' + data.status;
      });
    }

    function fetchClip() {
      document.getElementById('clipStatus').innerText = '⏳ Fetching...';
      document.getElementById('clipStatus').className = 'status';
      fetch('/get').then(r => r.json()).then(d => {
        document.getElementById('clipboardBox').value = d.text;
        document.getElementById('clipStatus').innerText = '✅ Fetched!';
        document.getElementById('clipStatus').className = 'status success';
      }).catch(e => {
        document.getElementById('clipStatus').innerText = '❌ Connection error';
        document.getElementById('clipStatus').className = 'status error';
      });
    }

    function copyToPhone() {
      const text = document.getElementById('clipboardBox').value;
      if (!text) {
        document.getElementById('clipStatus').innerText = '❌ No text to copy';
        document.getElementById('clipStatus').className = 'status error';
        return;
      }

      // Try modern clipboard API first
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          document.getElementById('clipStatus').innerText = '✅ Copied to phone!';
          document.getElementById('clipStatus').className = 'status success';
        }).catch(() => {
          fallbackCopy(text);
        });
      } else {
        fallbackCopy(text);
      }
    }

    function fallbackCopy(text) {
      const textarea = document.getElementById('clipboardBox');
      textarea.select();
      try {
        document.execCommand('copy');
        document.getElementById('clipStatus').innerText = '✅ Copied to phone!';
        document.getElementById('clipStatus').className = 'status success';
      } catch (err) {
        document.getElementById('clipStatus').innerText = '❌ Copy failed';
        document.getElementById('clipStatus').className = 'status error';
      }
    }

    function toggleLiveCapture() {
      isLiveCapturing = !isLiveCapturing;
      const btn = document.getElementById('toggleBtn');
      
      if (isLiveCapturing) {
        btn.innerText = 'Live OFF';
        btn.classList.add('active');
        document.getElementById('liveBox').value = '';
        document.getElementById('liveStatus').innerText = '🔴 Capturing keystrokes...';
        document.getElementById('liveStatus').className = 'status warning';
        socket.emit('start_capture');
      } else {
        btn.innerText = 'Live ON';
        btn.classList.remove('active');
        document.getElementById('liveStatus').innerText = '⚪ Capture disabled';
        document.getElementById('liveStatus').className = 'status';
        document.getElementById('modeLabel').innerText = '';
        socket.emit('stop_capture');
      }
    }

    function clearLiveBox() {
      document.getElementById('liveBox').value = '';
      document.getElementById('liveStatus').innerText = '';
    }

    function copyLiveBox() {
      const text = document.getElementById('liveBox').value;
      if (!text) {
        document.getElementById('liveStatus').innerText = '❌ No text to copy';
        document.getElementById('liveStatus').className = 'status error';
        return;
      }

      // Try modern clipboard API first
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
          document.getElementById('liveStatus').innerText = '✅ Copied!';
          document.getElementById('liveStatus').className = 'status success';
        }).catch(() => {
          fallbackCopyLive(text);
        });
      } else {
        fallbackCopyLive(text);
      }
    }

    function fallbackCopyLive(text) {
      const textarea = document.getElementById('liveBox');
      textarea.select();
      try {
        document.execCommand('copy');
        document.getElementById('liveStatus').innerText = '✅ Copied!';
        document.getElementById('liveStatus').className = 'status success';
      } catch (err) {
        document.getElementById('liveStatus').innerText = '❌ Copy failed';
        document.getElementById('liveStatus').className = 'status error';
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
