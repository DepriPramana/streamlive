# Database Migration Guide

## Problem
Jika Anda sudah punya database lama (`streaming.db`), akan muncul error:
```
sqlite3.OperationalError: no such column: stream_channels.start_date
```

Ini karena database lama tidak punya kolom baru yang ditambahkan.

## Solution

### Option 1: Migrasi Database (Recommended - Data Tetap Ada)

Jalankan script migrasi:

```bash
python migrate_database.py
```

Script ini akan:
- ✅ Menambahkan kolom baru ke tabel yang sudah ada
- ✅ Data lama tetap aman
- ✅ Channels yang sudah ada tetap berfungsi

### Option 2: Reset Database (Data Akan Hilang)

Jika tidak ada data penting, hapus database dan buat baru:

**Windows:**
```cmd
del streaming.db
python app.py
```

**Linux/Mac:**
```bash
rm streaming.db
python3 app.py
```

Database baru akan dibuat otomatis dengan schema terbaru.

## Kolom Baru yang Ditambahkan

1. **start_date** - Tanggal mulai campaign (opsional)
2. **end_date** - Tanggal selesai campaign (opsional)
3. **encoding_mode** - Mode encoding: 'copy' atau 'encode'
4. **fps** - Frame per second (default: 30)
5. **preset** - FFmpeg preset (default: 'veryfast')

## Verifikasi

Setelah migrasi, cek apakah berhasil:

```bash
python app.py
```

Buka browser: `http://localhost:5000`

Jika tidak ada error, migrasi berhasil! ✅
