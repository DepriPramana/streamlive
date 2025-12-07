/**
 * StreamLive Admin Dashboard JavaScript
 * Version: 2.0.0
 * Author: StreamLive Team
 */

// ===================================
// Global State Management
// ===================================
const AppState = {
    currentSection: 'dashboard',
    selectedVideoId: null,
    updateIntervals: {},
    
    init() {
        this.setupEventListeners();
        this.startAutoUpdates();
        this.showSection('dashboard');
    },
    
    setupEventListeners() {
        // Close modals on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeAllModals();
            }
        });
        
        // ESC key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    },
    
    startAutoUpdates() {
        // Update dashboard stats every 10 seconds (reduced from 5)
        this.updateIntervals.stats = setInterval(() => {
            if (this.currentSection === 'dashboard') {
                DashboardModule.updateStats();
            }
        }, 10000);
        
        // Update channels every 10 seconds (reduced from 3)
        this.updateIntervals.channels = setInterval(() => {
            if (this.currentSection === 'channels') {
                ChannelsModule.updateChannels();
            }
        }, 10000);
        
        // Update videos every 30 seconds (reduced from 5)
        this.updateIntervals.videos = setInterval(() => {
            if (this.currentSection === 'videos') {
                VideosModule.updateVideos();
            }
        }, 30000);
        
        // Update logs every 10 seconds (reduced from 3)
        this.updateIntervals.logs = setInterval(() => {
            if (this.currentSection === 'logs') {
                LogsModule.updateLogs();
            }
        }, 10000);
    },
    
    showSection(section) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(s => {
            s.classList.remove('active');
        });
        
        // Remove active from menu
        document.querySelectorAll('.menu-item').forEach(m => {
            m.classList.remove('active');
        });
        
        // Show selected section
        const sectionEl = document.getElementById(`section-${section}`);
        if (sectionEl) {
            sectionEl.classList.add('active');
        }
        
        // Add active to menu
        const menuItem = document.querySelector(`[data-section="${section}"]`);
        if (menuItem) {
            menuItem.classList.add('active');
        }
        
        // Update title
        const titles = {
            'dashboard': 'Dashboard',
            'channels': 'Channels Management',
            'videos': 'Video Library',
            'logs': 'System Logs',
            'stats': 'Statistics',
            'playlists': 'Video Playlists',
            'scheduler': 'Automated Scheduler',
            'platforms': 'Multi-Platform Streaming',
            'analytics': 'Advanced Analytics',
            'users': 'User Management'
        };
        document.getElementById('page-title').textContent = titles[section] || 'Dashboard';
        
        this.currentSection = section;
        
        // Load section data
        this.loadSectionData(section);
    },
    
    loadSectionData(section) {
        switch(section) {
            case 'dashboard':
                DashboardModule.updateStats();
                break;
            case 'channels':
                ChannelsModule.updateChannels();
                break;
            case 'videos':
                VideosModule.updateVideos();
                break;
            case 'logs':
                LogsModule.updateLogs();
                break;
            case 'stats':
                StatsModule.updateStats();
                break;
            case 'playlists':
                PlaylistsModule.updatePlaylists();
                break;
            case 'scheduler':
                SchedulerModule.updateTasks();
                break;
            case 'platforms':
                PlatformsModule.updatePlatforms();
                break;
            case 'analytics':
                AnalyticsModule.loadAnalytics();
                break;
            case 'users':
                if (typeof UsersModule !== 'undefined') {
                    UsersModule.updateUsers();
                }
                break;
        }
    },
    
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }
};

// ===================================
// Dashboard Module
// ===================================
const DashboardModule = {
    updateStats() {
        // Update channels count
        API.get('/channels').then(data => {
            Utils.updateElement('stat-channels', data.channels ? data.channels.length : 0);
        });
        
        // Update running streams
        API.get('/status').then(data => {
            Utils.updateElement('stat-running', data.total_running || 0);
        });
        
        // Update videos count and storage
        API.get('/videos').then(data => {
            const videos = data.videos || [];
            Utils.updateElement('stat-videos', videos.length);
            
            const totalSize = videos.reduce((sum, v) => sum + (v.file_size_mb || 0), 0);
            Utils.updateElement('stat-storage', (totalSize / 1024).toFixed(2) + 'GB');
        });
        
        // Update sessions and duration
        API.get('/stats').then(data => {
            Utils.updateElement('stat-sessions', data.total_sessions || 0);
            const hours = Math.floor((data.total_duration_seconds || 0) / 3600);
            Utils.updateElement('stat-duration', hours + 'h');
        });
        
        // Update system metrics
        this.updateSystemMetrics();
    },
    
    updateSystemMetrics() {
        API.get('/system/metrics').then(data => {
            if (!data.success) return;
            
            // Update CPU
            Utils.updateElement('system-cpu', data.cpu.percent + '%');
            const cpuBar = document.getElementById('cpu-progress');
            if (cpuBar) {
                cpuBar.style.width = data.cpu.percent + '%';
                cpuBar.className = 'progress-bar ' + this.getProgressClass(data.cpu.percent);
            }
            
            // Update Memory
            Utils.updateElement('system-memory', data.memory.percent + '%');
            Utils.updateElement('system-memory-detail', 
                `${data.memory.used_gb}GB / ${data.memory.total_gb}GB`);
            const memBar = document.getElementById('memory-progress');
            if (memBar) {
                memBar.style.width = data.memory.percent + '%';
                memBar.className = 'progress-bar ' + this.getProgressClass(data.memory.percent);
            }
            
            // Update Disk
            Utils.updateElement('system-disk', data.disk.percent + '%');
            Utils.updateElement('system-disk-detail', 
                `${data.disk.used_gb}GB / ${data.disk.total_gb}GB`);
            const diskBar = document.getElementById('disk-progress');
            if (diskBar) {
                diskBar.style.width = data.disk.percent + '%';
                diskBar.className = 'progress-bar ' + this.getProgressClass(data.disk.percent);
            }
        });
    },
    
    getProgressClass(percent) {
        if (percent < 50) return 'progress-success';
        if (percent < 75) return 'progress-warning';
        return 'progress-danger';
    }
};

// ===================================
// Channels Module
// ===================================
const ChannelsModule = {
    showAddModal() {
        document.getElementById('add-channel-modal').classList.add('active');
        VideosModule.updateVideos(); // Refresh video list
    },
    
    hideAddModal() {
        document.getElementById('add-channel-modal').classList.remove('active');
        document.getElementById('add-channel-form').reset();
        VideosModule.selectedVideoId = null;
    },
    
    addChannel(e) {
        e.preventDefault();
        
        const startDate = document.getElementById('new_start_date').value;
        const endDate = document.getElementById('new_end_date').value;
        
        if (startDate && endDate && new Date(startDate) > new Date(endDate)) {
            alert('❌ Start date cannot be greater than end date!');
            return;
        }
        
        const channel = {
            name: document.getElementById('new_channel_name').value,
            stream_key: document.getElementById('new_stream_key').value,
            video_path: document.getElementById('new_video_path').value,
            start_date: startDate || null,
            end_date: endDate || null,
            start_time: document.getElementById('new_start_time').value,
            end_time: document.getElementById('new_end_time').value,
            timezone: document.getElementById('new_timezone').value,
            encoding_mode: document.getElementById('new_encoding_mode').value,
            bitrate: document.getElementById('new_bitrate').value,
            fps: parseInt(document.getElementById('new_fps').value),
            preset: document.getElementById('new_preset').value
        };
        
        if (!channel.video_path) {
            alert('❌ Please select a video from library!');
            return;
        }
        
        API.post('/channels', channel).then(data => {
            alert(data.success ? '✅ ' + data.message : '❌ ' + data.message);
            if (data.success) {
                this.hideAddModal();
                this.updateChannels();
            }
        });
    },
    
    stopAll() {
        if (confirm('Stop all running streams?')) {
            API.post('/stop-all').then(data => {
                alert('✅ ' + data.message);
                this.updateChannels();
            });
        }
    },
    
    toggleAdvanced() {
        const checkbox = document.getElementById('show_advanced');
        const advancedDiv = document.getElementById('advanced_settings');
        advancedDiv.style.display = checkbox.checked ? 'block' : 'none';
    },
    
    toggleEncodingOptions() {
        const mode = document.getElementById('new_encoding_mode').value;
        const optionsDiv = document.getElementById('encoding_options');
        optionsDiv.style.display = mode === 'encode' ? 'block' : 'none';
    },
    
    updateChannels() {
        Promise.all([
            API.get('/channels'),
            API.get('/status')
        ]).then(([channelsData, statusData]) => {
            const container = document.getElementById('channels-container');
            if (!container) return;
            
            if (!channelsData.channels || channelsData.channels.length === 0) {
                container.innerHTML = '<div class="info-row">Belum ada channel. Tambah channel baru!</div>';
                return;
            }
            
            container.innerHTML = channelsData.channels.map(channel => {
                const channelStatus = statusData.channels?.find(c => c.id === channel.id);
                const isRunning = channelStatus ? channelStatus.running : false;
                
                return `
                    <div class="card" style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h3 style="margin: 0;">${channel.name}</h3>
                            <span class="status-badge status-${isRunning ? 'streaming' : 'stopped'}">
                                ${isRunning ? '🔴 Streaming' : '⚫ Stopped'}
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Schedule:</span>
                            <span class="info-value">${channel.start_time} - ${channel.end_time}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Video:</span>
                            <span class="info-value">${channelStatus?.video_exists ? '✅ Ready' : '❌ Missing'}</span>
                        </div>
                        <div style="margin-top: 15px;">
                            <button class="btn btn-success btn-sm" onclick="ChannelsModule.startChannel(${channel.id})" ${isRunning ? 'disabled' : ''}>
                                ▶️ Start
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="ChannelsModule.stopChannel(${channel.id})" ${!isRunning ? 'disabled' : ''}>
                                ⏹️ Stop
                            </button>
                            <button class="btn btn-secondary btn-sm" onclick="ChannelsModule.deleteChannel(${channel.id})" ${isRunning ? 'disabled' : ''}>
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        });
    },
    
    startChannel(id) {
        API.post(`/start/${id}`).then(data => {
            Utils.showNotification(data.message, data.success ? 'success' : 'error');
            this.updateChannels();
        });
    },
    
    stopChannel(id) {
        API.post(`/stop/${id}`).then(data => {
            Utils.showNotification(data.message, data.success ? 'success' : 'error');
            this.updateChannels();
        });
    },
    
    deleteChannel(id) {
        if (confirm('Are you sure you want to delete this channel?')) {
            API.delete(`/channels/${id}`).then(data => {
                Utils.showNotification(data.message, data.success ? 'success' : 'error');
                this.updateChannels();
            });
        }
    }
};

// ===================================
// Videos Module
// ===================================
const VideosModule = {
    selectedVideoId: null,
    
    updateVideos() {
        API.get('/videos').then(data => {
            const container = document.getElementById('videos-container');
            if (!container) return;
            
            if (!data.videos || data.videos.length === 0) {
                container.innerHTML = '<div class="info-row">No videos yet. Add your first video!</div>';
                return;
            }
            
            container.innerHTML = data.videos.map(video => `
                <div class="info-row">
                    <div>
                        <strong>${video.title}</strong><br>
                        <small style="color: #666;">
                            ${video.resolution || 'Unknown'} • ${video.duration_formatted} • ${video.file_size_mb} MB
                            ${video.usage_count > 0 ? ` • Used ${video.usage_count}x` : ''}
                        </small>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="VideosModule.deleteVideo(${video.id})">
                        🗑️
                    </button>
                </div>
            `).join('');
            
            // Update video select in add channel modal
            this.updateVideoSelect(data.videos);
        });
    },
    
    updateVideoSelect(videos) {
        const select = document.getElementById('new_video_id');
        if (!select) return;
        
        const currentValue = this.selectedVideoId || select.value;
        select.innerHTML = '<option value="">-- Select from Video Library --</option>' +
            videos.map(v => {
                const selected = v.id == currentValue ? 'selected' : '';
                return `<option value="${v.id}" ${selected}>${v.title} (${v.file_size_mb}MB)</option>`;
            }).join('');
        
        if (currentValue) {
            select.value = currentValue;
        }
    },
    
    selectVideo() {
        const videoId = document.getElementById('new_video_id').value;
        this.selectedVideoId = videoId;
        
        if (!videoId) {
            document.getElementById('new_video_path').value = '';
            return;
        }
        
        API.get(`/videos/${videoId}`).then(data => {
            document.getElementById('new_video_path').value = data.video.file_path;
        });
    },
    
    showUploadModal() {
        document.getElementById('upload-video-modal').classList.add('active');
    },
    
    hideUploadModal() {
        document.getElementById('upload-video-modal').classList.remove('active');
        document.getElementById('upload-video-form').reset();
        document.getElementById('upload-progress').style.display = 'none';
    },
    
    showDownloadModal() {
        document.getElementById('download-video-modal').classList.add('active');
    },
    
    hideDownloadModal() {
        document.getElementById('download-video-modal').classList.remove('active');
        document.getElementById('download-video-form').reset();
    },
    
    uploadVideo(e) {
        e.preventDefault();
        
        const title = document.getElementById('upload_video_title').value;
        const fileInput = document.getElementById('upload_video_file');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('❌ Please select a video file!');
            return;
        }
        
        if (file.size > 2 * 1024 * 1024 * 1024) {
            alert('❌ File too large! Maximum 2GB');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        
        document.getElementById('upload-progress').style.display = 'block';
        document.getElementById('upload-btn').disabled = true;
        
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                const progressBar = document.getElementById('upload-progress-bar');
                progressBar.style.width = percentComplete + '%';
                progressBar.textContent = percentComplete + '%';
                document.getElementById('upload-status').textContent = 
                    `Uploading... ${(e.loaded / 1024 / 1024).toFixed(2)} MB / ${(e.total / 1024 / 1024).toFixed(2)} MB`;
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                alert('✅ ' + response.message);
                this.hideUploadModal();
                this.updateVideos();
            } else {
                const response = JSON.parse(xhr.responseText);
                alert('❌ ' + (response.message || 'Upload failed'));
            }
            document.getElementById('upload-btn').disabled = false;
        });
        
        xhr.addEventListener('error', () => {
            alert('❌ Upload error!');
            document.getElementById('upload-btn').disabled = false;
        });
        
        xhr.open('POST', '/api/videos/upload');
        xhr.send(formData);
    },
    
    downloadFromGDrive(e) {
        e.preventDefault();
        
        const video = {
            title: document.getElementById('gdrive_video_title').value,
            filename: document.getElementById('gdrive_video_filename').value,
            gdrive_file_id: document.getElementById('gdrive_video_id').value
        };
        
        API.post('/videos/download-gdrive', video).then(data => {
            alert('✅ ' + data.message);
            this.hideDownloadModal();
            setTimeout(() => this.updateVideos(), 2000);
        });
    },
    
    scanLocal() {
        if (confirm('Scan ./videos folder for unregistered videos?')) {
            API.post('/videos/scan').then(data => {
                if (data.success) {
                    alert(`✅ ${data.message}\n\nFound: ${data.found} videos\nAdded: ${data.added} new videos`);
                    this.updateVideos();
                } else {
                    alert('❌ ' + data.message);
                }
            });
        }
    },
    
    deleteVideo(id) {
        if (confirm('Delete this video? This action cannot be undone!')) {
            API.delete(`/videos/${id}`).then(data => {
                Utils.showNotification(data.message, data.success ? 'success' : 'error');
                this.updateVideos();
            });
        }
    }
};

// ===================================
// Logs Module
// ===================================
const LogsModule = {
    updateLogs() {
        API.get('/logs').then(data => {
            const container = document.getElementById('log-container');
            if (!container) return;
            
            container.innerHTML = (data.logs || []).map(log => 
                `<div class="log-entry">${log}</div>`
            ).join('') || '<div class="log-entry">No logs yet...</div>';
            
            container.scrollTop = container.scrollHeight;
        });
    }
};

// ===================================
// Stats Module
// ===================================
const StatsModule = {
    updateStats() {
        // Update detailed statistics
        API.get('/stats').then(data => {
            Utils.updateElement('total-sessions', data.total_sessions || 0);
            const hours = Math.floor((data.total_duration_seconds || 0) / 3600);
            const minutes = Math.floor(((data.total_duration_seconds || 0) % 3600) / 60);
            Utils.updateElement('total-duration', `${hours}h ${minutes}m`);
        });
        
        // Update history
        API.get('/history?limit=5').then(data => {
            const container = document.getElementById('history-container');
            if (!container) return;
            
            if (!data.sessions || data.sessions.length === 0) {
                container.innerHTML = '<div class="info-row">No history yet</div>';
                return;
            }
            
            container.innerHTML = data.sessions.map(s => {
                const startTime = new Date(s.start_time).toLocaleString('id-ID');
                return `
                    <div class="info-row">
                        <span class="info-label">${startTime}</span>
                        <span class="info-value">${s.duration_formatted}</span>
                    </div>
                `;
            }).join('');
        });
    }
};

// ===================================
// Users Module (Admin Only)
// ===================================
const UsersModule = {
    showAddModal() {
        document.getElementById('add-user-modal').classList.add('active');
    },
    
    hideAddModal() {
        document.getElementById('add-user-modal').classList.remove('active');
        document.getElementById('add-user-form').reset();
    },
    
    showEditModal(user) {
        document.getElementById('edit_user_id').value = user.id;
        document.getElementById('edit_user_username').value = user.username;
        document.getElementById('edit_user_email').value = user.email || '';
        document.getElementById('edit_user_is_admin').checked = user.is_admin;
        document.getElementById('edit_user_is_active').checked = user.is_active;
        document.getElementById('edit_user_password').value = '';
        document.getElementById('edit-user-modal').classList.add('active');
    },
    
    hideEditModal() {
        document.getElementById('edit-user-modal').classList.remove('active');
        document.getElementById('edit-user-form').reset();
    },
    
    addUser(e) {
        e.preventDefault();
        
        const user = {
            username: document.getElementById('new_user_username').value,
            password: document.getElementById('new_user_password').value,
            email: document.getElementById('new_user_email').value,
            is_admin: document.getElementById('new_user_is_admin').checked,
            is_active: document.getElementById('new_user_is_active').checked
        };
        
        API.post('/users', user).then(data => {
            if (data.success) {
                alert('✅ ' + data.message);
                this.hideAddModal();
                this.updateUsers();
            } else {
                alert('❌ ' + data.message);
            }
        });
    },
    
    updateUser(e) {
        e.preventDefault();
        
        const userId = document.getElementById('edit_user_id').value;
        const password = document.getElementById('edit_user_password').value;
        
        const user = {
            username: document.getElementById('edit_user_username').value,
            email: document.getElementById('edit_user_email').value,
            is_admin: document.getElementById('edit_user_is_admin').checked,
            is_active: document.getElementById('edit_user_is_active').checked
        };
        
        // Only include password if it's not empty
        if (password) {
            user.password = password;
        }
        
        API.put(`/users/${userId}`, user).then(data => {
            if (data.success) {
                alert('✅ ' + data.message);
                this.hideEditModal();
                this.updateUsers();
            } else {
                alert('❌ ' + data.message);
            }
        });
    },
    
    deleteUser(id, username) {
        if (confirm(`Delete user "${username}"? This action cannot be undone!`)) {
            API.delete(`/users/${id}`).then(data => {
                if (data.success) {
                    alert('✅ ' + data.message);
                    this.updateUsers();
                } else {
                    alert('❌ ' + data.message);
                }
            });
        }
    },
    
    updateUsers() {
        API.get('/users').then(data => {
            const container = document.getElementById('users-container');
            if (!container) return;
            
            if (!data.users || data.users.length === 0) {
                container.innerHTML = '<div class="info-row">No users found</div>';
                return;
            }
            
            container.innerHTML = data.users.map(user => {
                const lastLogin = user.last_login ? 
                    new Date(user.last_login).toLocaleString('id-ID') : 
                    'Never';
                
                return `
                    <div class="card" style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <div>
                                <h3 style="margin: 0;">${user.username}</h3>
                                <small style="color: #666;">${user.email || 'No email'}</small>
                            </div>
                            <div>
                                ${user.is_admin ? '<span class="status-badge" style="background: #667eea;">👑 Admin</span>' : ''}
                                <span class="status-badge status-${user.is_active ? 'streaming' : 'stopped'}">
                                    ${user.is_active ? '✅ Active' : '❌ Inactive'}
                                </span>
                            </div>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Last Login:</span>
                            <span class="info-value">${lastLogin}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Created:</span>
                            <span class="info-value">${new Date(user.created_at).toLocaleDateString('id-ID')}</span>
                        </div>
                        <div style="margin-top: 15px;">
                            <button class="btn btn-primary btn-sm" onclick='UsersModule.showEditModal(${JSON.stringify(user).replace(/'/g, "&apos;")})'>
                                ✏️ Edit
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="UsersModule.deleteUser(${user.id}, '${user.username}')">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        });
    }
};

// ===================================
// API Helper
// ===================================
const API = {
    async get(endpoint) {
        try {
            const response = await fetch(`/api${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return {};
        }
    },
    
    async post(endpoint, data = {}) {
        try {
            const response = await fetch(`/api${endpoint}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return {success: false, message: error.message};
        }
    },
    
    async put(endpoint, data = {}) {
        try {
            const response = await fetch(`/api${endpoint}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return {success: false, message: error.message};
        }
    },
    
    async delete(endpoint) {
        try {
            const response = await fetch(`/api${endpoint}`, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return {success: false, message: error.message};
        }
    }
};

// ===================================
// Utilities
// ===================================
const Utils = {
    updateElement(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    },
    
    showNotification(message, type = 'info') {
        // Simple alert for now, can be enhanced with toast notifications
        alert(message);
    }
};

// ===================================
// Playlists Module
// ===================================
const PlaylistsModule = {
    showAddModal() {
        document.getElementById('add-playlist-modal').classList.add('active');
    },
    
    hideAddModal() {
        document.getElementById('add-playlist-modal').classList.remove('active');
        document.getElementById('add-playlist-form').reset();
    },
    
    addPlaylist(e) {
        e.preventDefault();
        
        const playlist = {
            name: document.getElementById('new_playlist_name').value,
            description: document.getElementById('new_playlist_description').value,
            playback_mode: document.getElementById('new_playlist_mode').value
        };
        
        API.post('/playlists', playlist).then(data => {
            if (data.success) {
                alert('✅ Playlist created successfully!');
                this.hideAddModal();
                this.updatePlaylists();
            } else {
                alert('❌ ' + (data.message || 'Failed to create playlist'));
            }
        });
    },
    
    updatePlaylists() {
        API.get('/playlists').then(data => {
            const container = document.getElementById('playlists-container');
            if (!container) return;
            
            if (!data.playlists || data.playlists.length === 0) {
                container.innerHTML = '<div class="info-row">No playlists yet. Create your first playlist!</div>';
                return;
            }
            
            container.innerHTML = data.playlists.map(playlist => `
                <div class="card" style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div>
                            <h3 style="margin: 0;">${playlist.name}</h3>
                            <small style="color: #666;">${playlist.description || 'No description'}</small>
                        </div>
                        <span class="status-badge" style="background: #667eea;">
                            ${playlist.video_count} videos
                        </span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Mode:</span>
                        <span class="info-value">${playlist.playback_mode}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <button class="btn btn-primary btn-sm" onclick="PlaylistsModule.viewPlaylist(${playlist.id})">
                            👁️ View
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="PlaylistsModule.deletePlaylist(${playlist.id})">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            `).join('');
        });
    },
    
    viewPlaylist(id) {
        alert('Playlist details view - Coming soon!');
    },
    
    deletePlaylist(id) {
        if (confirm('Delete this playlist?')) {
            API.delete(`/playlists/${id}`).then(data => {
                alert(data.success ? '✅ Playlist deleted' : '❌ ' + data.message);
                this.updatePlaylists();
            });
        }
    }
};

// ===================================
// Scheduler Module
// ===================================
const SchedulerModule = {
    showAddModal() {
        // Load channels first
        API.get('/channels').then(data => {
            const select = document.getElementById('new_task_channel');
            select.innerHTML = '<option value="">-- Select Channel --</option>' +
                (data.channels || []).map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        });
        document.getElementById('add-scheduler-modal').classList.add('active');
    },
    
    hideAddModal() {
        document.getElementById('add-scheduler-modal').classList.remove('active');
        document.getElementById('add-scheduler-form').reset();
    },
    
    addTask(e) {
        e.preventDefault();
        
        const days = Array.from(document.querySelectorAll('.task-day:checked'))
            .map(cb => cb.value).join(',');
        
        const task = {
            channel_id: parseInt(document.getElementById('new_task_channel').value),
            task_type: document.getElementById('new_task_type').value,
            scheduled_time: document.getElementById('new_task_time').value,
            days_of_week: days
        };
        
        API.post('/scheduled-tasks', task).then(data => {
            if (data.success) {
                alert('✅ Task scheduled successfully!');
                this.hideAddModal();
                this.updateTasks();
            } else {
                alert('❌ ' + (data.message || 'Failed to create task'));
            }
        });
    },
    
    updateTasks() {
        API.get('/scheduled-tasks').then(data => {
            const container = document.getElementById('scheduler-container');
            if (!container) return;
            
            if (!data.tasks || data.tasks.length === 0) {
                container.innerHTML = '<div class="info-row">No scheduled tasks. Add your first task!</div>';
                return;
            }
            
            const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            
            container.innerHTML = data.tasks.map(task => {
                const days = task.days_of_week.split(',').map(d => dayNames[parseInt(d)]).join(', ');
                const icon = task.task_type === 'start' ? '▶️' : '⏹️';
                
                return `
                    <div class="card" style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <h3 style="margin: 0;">${icon} ${task.task_type.toUpperCase()} - ${task.channel_name}</h3>
                            </div>
                            <span class="status-badge status-${task.enabled ? 'streaming' : 'stopped'}">
                                ${task.enabled ? '✅ Enabled' : '❌ Disabled'}
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Time:</span>
                            <span class="info-value">${task.scheduled_time}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Days:</span>
                            <span class="info-value">${days}</span>
                        </div>
                        ${task.last_run ? `
                        <div class="info-row">
                            <span class="info-label">Last Run:</span>
                            <span class="info-value">${new Date(task.last_run).toLocaleString()}</span>
                        </div>
                        ` : ''}
                        <div style="margin-top: 10px;">
                            <button class="btn btn-danger btn-sm" onclick="SchedulerModule.deleteTask(${task.id})">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        });
    },
    
    deleteTask(id) {
        if (confirm('Delete this scheduled task?')) {
            API.delete(`/scheduled-tasks/${id}`).then(data => {
                alert(data.success ? '✅ Task deleted' : '❌ ' + data.message);
                this.updateTasks();
            });
        }
    }
};

// ===================================
// Platforms Module
// ===================================
const PlatformsModule = {
    showAddModal() {
        // Load channels first
        API.get('/channels').then(data => {
            const select = document.getElementById('new_platform_channel');
            select.innerHTML = '<option value="">-- Select Channel --</option>' +
                (data.channels || []).map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        });
        document.getElementById('add-platform-modal').classList.add('active');
    },
    
    hideAddModal() {
        document.getElementById('add-platform-modal').classList.remove('active');
        document.getElementById('add-platform-form').reset();
    },
    
    updateRTMPUrl() {
        const platform = document.getElementById('new_platform_name').value;
        const rtmpInput = document.getElementById('new_platform_rtmp');
        
        const urls = {
            'youtube': 'rtmp://a.rtmp.youtube.com/live2/',
            'facebook': 'rtmps://live-api-s.facebook.com:443/rtmp/',
            'twitch': 'rtmp://live.twitch.tv/app/'
        };
        
        if (urls[platform]) {
            rtmpInput.value = urls[platform];
        } else {
            rtmpInput.value = '';
        }
    },
    
    addPlatform(e) {
        e.preventDefault();
        
        const platform = {
            channel_id: parseInt(document.getElementById('new_platform_channel').value),
            platform_name: document.getElementById('new_platform_name').value,
            rtmp_url: document.getElementById('new_platform_rtmp').value,
            stream_key: document.getElementById('new_platform_key').value,
            priority: parseInt(document.getElementById('new_platform_priority').value)
        };
        
        API.post('/platforms', platform).then(data => {
            if (data.success) {
                alert('✅ Platform added successfully!');
                this.hideAddModal();
                this.updatePlatforms();
            } else {
                alert('❌ ' + (data.message || 'Failed to add platform'));
            }
        });
    },
    
    updatePlatforms() {
        API.get('/platforms').then(data => {
            const container = document.getElementById('platforms-container');
            if (!container) return;
            
            if (!data.platforms || data.platforms.length === 0) {
                container.innerHTML = '<div class="info-row">No platforms configured. Add your first platform!</div>';
                return;
            }
            
            // Group by channel
            const byChannel = {};
            data.platforms.forEach(p => {
                if (!byChannel[p.channel_id]) {
                    byChannel[p.channel_id] = [];
                }
                byChannel[p.channel_id].push(p);
            });
            
            let html = '';
            for (const channelId in byChannel) {
                const platforms = byChannel[channelId];
                const channelName = platforms[0].channel_name || `Channel ${channelId}`;
                
                html += `
                    <div class="card" style="margin-bottom: 20px;">
                        <h3 style="margin-bottom: 15px;">📺 ${channelName}</h3>
                        ${platforms.map(p => `
                            <div class="info-row" style="border-bottom: 1px solid #eee; padding: 10px 0;">
                                <div>
                                    <strong>${this.getPlatformIcon(p.platform_name)} ${p.platform_name.toUpperCase()}</strong><br>
                                    <small style="color: #666;">Key: ${p.stream_key}</small>
                                </div>
                                <div>
                                    <span class="status-badge status-${p.enabled ? 'streaming' : 'stopped'}">
                                        ${p.enabled ? '✅ Enabled' : '❌ Disabled'}
                                    </span>
                                    <button class="btn btn-danger btn-sm" onclick="PlatformsModule.deletePlatform(${p.id})" style="margin-left: 10px;">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            container.innerHTML = html;
        });
    },
    
    getPlatformIcon(platform) {
        const icons = {
            'youtube': '📺',
            'facebook': '👥',
            'twitch': '🎮',
            'custom': '📡'
        };
        return icons[platform] || '📡';
    },
    
    deletePlatform(id) {
        if (confirm('Delete this platform destination?')) {
            API.delete(`/platforms/${id}`).then(data => {
                alert(data.success ? '✅ Platform deleted' : '❌ ' + data.message);
                this.updatePlatforms();
            });
        }
    }
};

// ===================================
// Analytics Module
// ===================================
const AnalyticsModule = {
    loadAnalytics() {
        const channelId = document.getElementById('analytics-channel-select').value;
        const days = document.getElementById('analytics-days-select').value;
        
        // Load channel analytics
        if (channelId) {
            API.get(`/analytics/channel/${channelId}?days=${days}`).then(data => {
                this.displayChannelAnalytics(data);
            });
        }
        
        // Load peak hours
        const peakUrl = channelId ? 
            `/analytics/peak-hours?channel_id=${channelId}&days=${days}` :
            `/analytics/peak-hours?days=${days}`;
        API.get(peakUrl).then(data => {
            this.displayPeakHours(data);
        });
        
        // Load video performance
        API.get(`/analytics/video-performance?days=${days}`).then(data => {
            this.displayVideoPerformance(data);
        });
    },
    
    displayChannelAnalytics(data) {
        Utils.updateElement('analytics-total-sessions', data.total_sessions || 0);
        Utils.updateElement('analytics-success-rate', (data.success_rate || 0).toFixed(1) + '%');
        Utils.updateElement('analytics-uptime', (data.uptime_percentage || 0).toFixed(1) + '%');
        
        const avgHours = Math.floor((data.average_session_duration || 0) / 3600);
        const avgMins = Math.floor(((data.average_session_duration || 0) % 3600) / 60);
        Utils.updateElement('analytics-avg-duration', `${avgHours}h ${avgMins}m`);
    },
    
    displayPeakHours(data) {
        const container = document.getElementById('peak-hours-container');
        if (!container) return;
        
        if (!data.peak_hours || data.peak_hours.length === 0) {
            container.innerHTML = '<div class="info-row">No data available</div>';
            return;
        }
        
        container.innerHTML = data.peak_hours.map(h => `
            <div class="info-row">
                <span class="info-label">${h.hour}:00 - ${h.hour + 1}:00</span>
                <span class="info-value">${h.sessions} sessions</span>
            </div>
        `).join('');
    },
    
    displayVideoPerformance(data) {
        const container = document.getElementById('video-performance-container');
        if (!container) return;
        
        if (!data || data.length === 0) {
            container.innerHTML = '<div class="info-row">No data available</div>';
            return;
        }
        
        container.innerHTML = data.slice(0, 10).map(v => `
            <div class="info-row">
                <div>
                    <strong>${v.video_title}</strong><br>
                    <small style="color: #666;">Used ${v.usage_count} times</small>
                </div>
                <span class="info-value">${this.formatDuration(v.total_duration)}</span>
            </div>
        `).join('');
    },
    
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    },
    
    exportReport() {
        const channelId = document.getElementById('analytics-channel-select').value;
        const days = document.getElementById('analytics-days-select').value;
        
        let url = `/analytics/export?type=channel&days=${days}&format=json`;
        if (channelId) {
            url += `&channel_id=${channelId}`;
        }
        
        window.open('/api' + url, '_blank');
    },
    
    init() {
        // Load channels for select
        API.get('/channels').then(data => {
            const select = document.getElementById('analytics-channel-select');
            if (select && data.channels) {
                select.innerHTML = '<option value="">All Channels</option>' +
                    data.channels.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
            }
        });
    }
};

// ===================================
// Initialize App
// ===================================
document.addEventListener('DOMContentLoaded', () => {
    AppState.init();
    AnalyticsModule.init();
});
