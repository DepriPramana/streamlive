# Quick Start Guide - StreamLive Admin Dashboard

## 🚀 5-Minute Setup

### Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

**Important**: Make sure `psutil` is installed for system monitoring:
```bash
pip install psutil
```

### Step 2: Database Setup (30 seconds)

If you have an old database, migrate it:
```bash
python migrate_database.py
```

Or start fresh (delete old database):
```bash
# Windows
del streaming.db

# Linux/Mac
rm streaming.db
```

### Step 3: Start Application (10 seconds)

```bash
python app.py
```

### Step 4: Access Dashboard (10 seconds)

Open browser:
```
http://localhost:5000
```

## ✅ Verify Everything Works

### Quick Test (2 minutes)

1. **Dashboard loads** - You should see 6 stat cards
2. **System metrics show** - CPU, Memory, Disk with progress bars
3. **Click "Channels"** in sidebar - Section changes
4. **Click "Add New Channel"** - Modal opens
5. **Click "Videos"** in sidebar - Section changes
6. **Click "Upload Video"** - Modal opens

If all above work, you're good to go! ✅

## 🎯 First Time Usage

### Add Your First Video

1. Click **"Videos"** in sidebar
2. Click **"📤 Upload Video"** button
3. Fill in title and select video file
4. Click **"Upload"**
5. Wait for progress bar to complete

### Create Your First Channel

1. Click **"Channels"** in sidebar
2. Click **"➕ Add New Channel"** button
3. Fill in:
   - Channel Name
   - YouTube Stream Key (from YouTube Studio)
   - Select Video from dropdown
   - Set schedule times
4. Click **"💾 Save"**

### Start Streaming

1. Find your channel in the list
2. Click **"▶️ Start"** button
3. Check YouTube to verify stream is live!

## 🔧 Troubleshooting

### Problem: "Module not found: psutil"

**Solution:**
```bash
pip install psutil
```

### Problem: "No such column: start_date"

**Solution:**
```bash
python migrate_database.py
```

### Problem: Stats show 0

**Solution:**
- Wait 5 seconds for auto-update
- Or refresh page (Ctrl+F5)

### Problem: Modal doesn't open

**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)

### Problem: Can't upload video

**Solution:**
- Check file size (max 2GB)
- Ensure ./videos folder exists
- Check disk space

## 📱 Access from Other Devices

### Same Network

Find your IP address:

**Windows:**
```cmd
ipconfig
```

**Linux/Mac:**
```bash
ifconfig
```

Then access from other device:
```
http://YOUR_IP:5000
```

Example: `http://192.168.1.100:5000`

### Remote Access (Advanced)

Use ngrok or similar tunneling service:
```bash
ngrok http 5000
```

## 🎨 Interface Overview

### Sidebar Menu
- 📊 **Dashboard** - Overview & system metrics
- 📺 **Channels** - Manage streaming channels
- 🎬 **Video Library** - Upload & manage videos
- 📝 **System Logs** - View activity logs
- 📈 **Statistics** - Detailed analytics

### Dashboard Cards
1. **Total Channels** - Number of configured channels
2. **Running Streams** - Currently active streams
3. **Total Videos** - Videos in library
4. **Total Sessions** - All-time streaming sessions
5. **Total Duration** - Total hours streamed
6. **Storage Used** - Disk space used by videos

### System Metrics
- **CPU Usage** - Real-time processor usage
- **Memory Usage** - RAM consumption
- **Disk Usage** - Storage space used

## 💡 Pro Tips

1. **Upload videos first** before creating channels
2. **Use Copy mode** for better performance (in Advanced Settings)
3. **Set campaign dates** for scheduled streaming
4. **Monitor system metrics** to avoid overload
5. **Check logs** if something goes wrong

## 📚 Next Steps

- Read [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing
- Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture
- Review [README.md](README.md) for full documentation

## 🆘 Need Help?

1. Check console for errors (F12 in browser)
2. Review server logs in terminal
3. Read [TESTING_GUIDE.md](TESTING_GUIDE.md)
4. Check [MIGRATION.md](MIGRATION.md) for database issues

---

**Ready to stream!** 🎥✨

If everything works, you're all set. Happy streaming!
