# 📋 Clipboard Sync — Windows to iPhone/Android

Copy anything on your Windows laptop and paste it on your phone via a local web server. No cloud, no apps needed.

## ⚡ Quick Start (2 minutes)

### Option 1: Automatic (Easiest)
1. Double-click **`run.bat`** 
2. It will show your PC's IP address
3. Open that URL on your phone browser
4. Done!

### Option 2: Manual Steps

**Step 1: Install Dependencies**
```
pip install flask pyperclip
```

**Step 2: Find Your PC's IP Address**
Open PowerShell and run:
```
ipconfig
```
Find **IPv4 Address** (usually looks like `192.168.1.42`)

**Step 3: Start the Server**
```
python clip_server.py
```

**Step 4: Open on Your Phone**
- Connect phone to same WiFi as your PC
- Open Safari (iPhone) or Chrome (Android)
- Go to: `http://YOUR.PC.IP.ADDRESS:5055`

## 📱 How to Use

### Copy from Windows → Paste on iPhone
1. Copy anything on your PC (Ctrl+C)
   - Teams chat, email, browser, Word, Notepad — anything works
2. Open phone browser (bookmark it for speed)
3. Tap **"⬇️ Get from PC"** → content appears
4. Tap **"📲 Copy to Phone"** → added to phone clipboard
5. Paste anywhere normally (long press → Paste)

### Pro Tips
- **Bookmark on home screen**: Safari → Share → Add to Home Screen
- **Auto-refresh**: Tap "Get from PC" every time you copy something new
- **One message at a time**: Windows only stores what you last copied (not the app's limitation)

## ❓ FAQ

**Q: Works from Teams mails emails, etc?**  
A: Yes! Copy (Ctrl+C) from anywhere on Windows — the server reads your clipboard.

**Q: Is it instant?**  
A: Yes — no delay. You just need to tap the button on your phone.

**Q: Can I copy multiple messages?**  
A: One at a time (Windows limitation). Copy #1 → fetch → copy #2 → fetch.

**Q: It won't connect?**  
A: 
1. Both devices on same WiFi? ✅
2. Correct IP address? (run `ipconfig` again)
3. Allow Python through Windows Firewall if prompted
4. Try restarting the server

**Q: Only works on WiFi?**  
A: Yes, both must be on the same network.

## 🔧 Requirements
- Python 3.6+ (check: `python --version`)
- Both devices on same WiFi
- Phone browser (no app needed)

## 📝 License
Free to use, modify, share!
