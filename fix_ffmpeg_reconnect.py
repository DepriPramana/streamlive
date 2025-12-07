#!/usr/bin/env python3
"""
Patch untuk menambahkan reconnection logic ke FFmpeg
"""

# Tambahkan parameter reconnect ke FFmpeg command
RECONNECT_PARAMS = [
    '-reconnect', '1',
    '-reconnect_streamed', '1',
    '-reconnect_delay_max', '5',
    '-timeout', '10000000',  # 10 seconds
    '-rw_timeout', '10000000'  # 10 seconds read/write timeout
]

print("""
Untuk fix masalah reconnection, tambahkan parameter ini ke FFmpeg:

-reconnect 1
-reconnect_streamed 1  
-reconnect_delay_max 5
-timeout 10000000
-rw_timeout 10000000

Atau gunakan OBS Studio untuk streaming yang lebih stabil.
""")
