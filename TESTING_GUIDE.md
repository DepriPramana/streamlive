# Testing Guide - StreamLive Admin Dashboard

## 🧪 Pre-Flight Checklist

### 1. Install Dependencies

```bash
pip install psutil
```

### 2. Run Database Migration (if needed)

```bash
python migrate_database.py
```

### 3. Start Application

```bash
python app.py
```

Expected output:
```
Database initialized!
YouTube Live Stream Scheduler - Web Version
Akses web interface di: http://localhost:5000
```

## ✅ Testing Checklist

### Dashboard Section

**Stats Cards (Top Row):**
- [ ] Total Channels - Shows correct count
- [ ] Running Streams - Shows active streams
- [ ] Total Videos - Shows video count
- [ ] Total Sessions - Shows session count
- [ ] Total Duration - Shows hours
- [ ] Storage Used - Shows GB used

**System Metrics:**
- [ ] CPU Usage - Shows percentage with progress bar
- [ ] Memory Usage - Shows GB used / total
- [ ] Disk Usage - Shows GB used / total
- [ ] Progress bars change color (green/yellow/red)

**Auto-Update:**
- [ ] Stats update every 5 seconds
- [ ] System metrics update every 5 seconds

### Channels Section

**Display:**
- [ ] Shows "No channels" message if empty
- [ ] Lists all channels with status badges
- [ ] Shows schedule and video status

**Buttons:**
- [ ] "Add New Channel" opens modal
- [ ] "Stop All Streams" shows confirmation
- [ ] "Start" button works per channel
- [ ] "Stop" button works per channel
- [ ] "Delete" button works per channel

**Add Channel Modal:**
- [ ] Modal opens correctly
- [ ] Video dropdown populates
- [ ] Selecting video fills path
- [ ] Date validation works
- [ ] Advanced settings toggle works
- [ ] Encoding options toggle works
- [ ] Form submits successfully
- [ ] Modal closes after submit

### Videos Section

**Display:**
- [ ] Shows "No videos" message if empty
- [ ] Lists all videos with metadata
- [ ] Shows resolution, duration, file size
- [ ] Shows usage count

**Buttons:**
- [ ] "Upload Video" opens modal
- [ ] "Download from GDrive" opens modal
- [ ] "Scan Folder" shows confirmation
- [ ] "Delete" button works per video

**Upload Modal:**
- [ ] Modal opens correctly
- [ ] File input accepts videos
- [ ] Progress bar shows during upload
- [ ] Success message after upload
- [ ] Video list refreshes

**Download Modal:**
- [ ] Modal opens correctly
- [ ] Form validates inputs
- [ ] Download starts successfully
- [ ] Video appears in list after download

### Logs Section

**Display:**
- [ ] Shows log entries
- [ ] Auto-scrolls to bottom
- [ ] Updates every 3 seconds
- [ ] Shows timestamps

### Statistics Section

**Display:**
- [ ] Shows total sessions
- [ ] Shows total duration
- [ ] Shows recent history
- [ ] Updates correctly

## 🔍 API Testing

### Manual API Tests

Open browser console and run:

```javascript
// Test System Metrics
fetch('/api/system/metrics')
  .then(r => r.json())
  .then(d => console.log('System Metrics:', d));

// Test Channels
fetch('/api/channels')
  .then(r => r.json())
  .then(d => console.log('Channels:', d));

// Test Videos
fetch('/api/videos')
  .then(r => r.json())
  .then(d => console.log('Videos:', d));

// Test Status
fetch('/api/status')
  .then(r => r.json())
  .then(d => console.log('Status:', d));
```

### Automated API Tests

```bash
python test_api.py
```

Expected output:
```
✅ Main Dashboard: OK
✅ Channels API: OK
✅ Videos API: OK
✅ Status API: OK
✅ Stats API: OK
✅ System Metrics API: OK
```

## 🐛 Common Issues & Solutions

### Issue: Stats not updating

**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify API endpoints return data
4. Check network tab for failed requests

### Issue: System metrics show 0%

**Solution:**
1. Ensure psutil is installed: `pip install psutil`
2. Restart the application
3. Check `/api/system/metrics` endpoint directly

### Issue: Modals not opening

**Solution:**
1. Check browser console for errors
2. Verify admin.js is loaded
3. Clear browser cache (Ctrl+F5)

### Issue: Videos not uploading

**Solution:**
1. Check file size (max 2GB)
2. Verify ./videos folder exists
3. Check server logs for errors
4. Ensure sufficient disk space

### Issue: Channels not starting

**Solution:**
1. Verify video file exists
2. Check FFmpeg is installed
3. Verify stream key is correct
4. Check logs for error messages

## 📊 Performance Testing

### Load Test

1. Add multiple channels (5-10)
2. Start multiple streams simultaneously
3. Monitor system metrics
4. Check for memory leaks
5. Verify all streams running

### Stress Test

1. Upload large video files
2. Create many channels
3. Monitor CPU and memory
4. Check response times
5. Verify stability

## 🔐 Security Testing

### Basic Security Checks

- [ ] No sensitive data in console logs
- [ ] API endpoints validate inputs
- [ ] File uploads check file types
- [ ] SQL injection prevention (ORM)
- [ ] XSS protection in forms

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

Dashboard: ✅ / ❌
Channels: ✅ / ❌
Videos: ✅ / ❌
Logs: ✅ / ❌
Statistics: ✅ / ❌
System Metrics: ✅ / ❌

Issues Found:
1. ___________
2. ___________

Notes:
___________
```

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] All tests pass
- [ ] No console errors
- [ ] Database migrated
- [ ] Dependencies installed
- [ ] Config file updated
- [ ] Backup created
- [ ] Documentation updated
- [ ] Performance acceptable
- [ ] Security reviewed

## 📞 Support

If tests fail:
1. Check this guide
2. Review console errors
3. Check server logs
4. Verify dependencies
5. Restart application

---

**Last Updated**: December 2024  
**Version**: 2.0.0
