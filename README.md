# � Puppy — Wireless Clipboard Sync

Transfer text between your Windows PC and iPhone/Android **instantly** without cloud storage, apps, or complicated setup. Just copy on your PC, paste on your phone over WiFi.

## ✨ Features

- **📋 Clipboard Sync** — Copy on Windows (Ctrl+C) → Paste on iPhone/Android
- **⌨️ Live Typing Capture** — See everything you type on your PC appear on your phone in real-time
- **🔒 Local WiFi Only** — No cloud, no data tracking, 100% private
- **📱 Zero Apps Needed** — Works in any phone browser (Safari, Chrome)
- **⚡ No Setup Hassle** — Just run `run.bat` and open a URL
- **🎨 Split Panel UI** — Separate panels for clipboard and live typing

## 🚀 Quick Start (30 seconds)

### Windows
1. Install Python (if not already installed)
2. Double-click **`run.bat`**
3. You'll see: `Server running at http://192.168.X.X:5055`

### iPhone/Android
1. Make sure your phone is on **same WiFi** as your PC
2. Open Safari (iPhone) or Chrome (Android)
3. Go to: `http://192.168.X.X:5055` (replace with your PC's IP)
4. Bookmark for quick access!

## 📖 How to Use

### Mode 1: Clipboard Sync (Left Panel)
```
1. Copy anything on your PC (Ctrl+C)
   → Email, Teams chat, code, URLs, anything works
2. Tap "⬇️ Get from PC" on your phone
3. Text appears instantly
4. Tap "📲 Copy" to add to phone clipboard
5. Paste normally (long-press → Paste)
```

### Mode 2: Live Typing (Right Panel)
```
1. Tap "Live ON" button on your phone
2. Start typing ANYWHERE on your PC
   → Notepad, VS Code, Slack, email — it captures everything
3. Your text appears live on the phone screen
4. Tap "Copy" to copy what you typed
5. Tap "Clear" to reset
```

## 🛠️ Installation

### Method 1: Automatic (Windows)
```bash
run.bat
```

### Method 2: Manual
```bash
# Install dependencies
python -m pip install -r requirements.txt

# Start server
python clip_server.py
```

### Find Your PC's IP Address
Open PowerShell and run:
```bash
ipconfig
```
Look for **IPv4 Address** (e.g., `192.168.1.42`)

## 🔧 System Requirements

- **Windows 10/11** with Python 3.7+
- **iPhone** (any iOS with Safari) or **Android** (any phone with browser)
- Both devices on **same WiFi network**
- Port 5055 available (can be changed in code)

## ❓ FAQ

| Question | Answer |
|----------|--------|
| **Will it work from Teams/Gmail/Chrome?** | Yes! Ctrl+C from anywhere works |
| **Is it fast?** | Instant — no lag |
| **What about security?** | Local WiFi only, nothing stored, nothing sent to cloud |
| **Can multiple people use it?** | Yes, same network, any number of phones |
| **Does it work over internet?** | No, WiFi only (intentional for privacy) |
| **Can I transfer files?** | Currently text only; file sharing coming soon |

## 🐛 Troubleshooting

**"Cannot connect to server"**
- ✅ Both devices on same WiFi?
- ✅ Using correct IP? (Run `ipconfig` on PC)
- ✅ Did you include `:5055` at the end?

**"Windows Firewall is blocking"**
- Allow `python.exe` through Windows Defender Firewall

**"Server won't start"**
- Make sure port 5055 is free (no other app using it)
- Try: `netstat -ano | findstr :5055`

**"Live typing not working"**
- Make sure you clicked "Live ON" button
- Try pressing keys in a text app (Notepad, browser)

## 🏗️ Project Structure

```
puppy/
├── clip_server.py          # Main Flask + WebSocket server
├── requirements.txt        # Python dependencies
├── run.bat                 # Windows quick-start launcher
├── README.md              # This file
└── .gitignore            # Git ignore rules
```

## 📦 Dependencies

- **Flask** — Web server
- **flask-socketio** — WebSocket for real-time updates
- **pyperclip** — Read Windows clipboard
- **pynput** — Capture keyboard input

## 🎯 How It Works Under the Hood

1. **Clipboard Sync**: `pyperclip` reads your Windows clipboard when you tap "Get from PC"
2. **Live Typing**: `pynput.Listener` captures all keystrokes and sends via WebSocket
3. **WebSocket**: Maintains real-time connection between PC and phone
4. **Web UI**: React-free vanilla JavaScript for instant updates

## 🔮 Planned Features

- [ ] Clipboard history (last 20 items)
- [ ] Auto-sync mode (sync every 5 seconds)
- [ ] Dark mode
- [ ] File transfer
- [ ] Voice input
- [ ] Sync between multiple phones

## 🤝 Contributing

Found a bug? Have an idea? **Pull requests welcome!**

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

MIT License — Use, modify, and share freely!

## 🙋 Support

**Having issues?** Check the [Troubleshooting](#-troubleshooting) section or open an issue.

---

**Made with ❤️ for seamless PC-to-Phone text transfer**
