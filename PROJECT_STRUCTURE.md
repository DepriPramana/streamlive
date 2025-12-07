# StreamLive Project Structure

## 📁 Directory Structure

```
streamlive/
├── app.py                      # Main Flask application
├── database.py                 # Database models & ORM
├── migrate_database.py         # Database migration script
├── config.json                 # Application configuration
├── streaming.db                # SQLite database
│
├── static/                     # Static assets
│   ├── css/
│   │   └── admin.css          # Admin dashboard styles
│   └── js/
│       └── admin.js           # Admin dashboard JavaScript
│
├── templates/                  # HTML templates
│   ├── admin.html             # Professional admin dashboard
│   └── index.html             # Simple view (legacy)
│
├── videos/                     # Video storage directory
│
└── docs/                       # Documentation
    ├── README.md
    ├── MIGRATION.md
    ├── CHANGELOG.md
    └── PROJECT_STRUCTURE.md
```

## 🏗️ Architecture

### Backend (Python/Flask)
- **app.py**: Main application with routes and API endpoints
- **database.py**: SQLAlchemy models for data persistence
- **migrate_database.py**: Database schema migration utilities

### Frontend (HTML/CSS/JS)
- **admin.html**: Modern admin dashboard with sidebar navigation
- **admin.css**: Modular, maintainable CSS with CSS variables
- **admin.js**: Organized JavaScript with module pattern

### Database (SQLite)
- **StreamChannel**: Channel configurations
- **VideoLibrary**: Video metadata and storage
- **StreamSession**: Streaming session history
- **StreamLog**: System logs
- **StreamStats**: Daily statistics
- **Configuration**: App settings

## 🎯 Design Patterns

### JavaScript Modules
```javascript
- AppState: Global state management
- DashboardModule: Dashboard functionality
- ChannelsModule: Channel management
- VideosModule: Video library management
- LogsModule: System logs
- StatsModule: Statistics & analytics
- API: Centralized API communication
- Utils: Helper functions
```

### CSS Architecture
```css
- CSS Variables: Centralized theming
- BEM-like naming: Consistent class names
- Mobile-first: Responsive design
- Animations: Smooth transitions
```

### Backend Structure
```python
- StreamManager: Core streaming logic
- Route handlers: RESTful API endpoints
- Database models: ORM entities
- Helper functions: Utilities
```

## 🔄 Data Flow

```
User Action (UI)
    ↓
JavaScript Module
    ↓
API Helper (fetch)
    ↓
Flask Route Handler
    ↓
StreamManager / Database
    ↓
JSON Response
    ↓
JavaScript Module
    ↓
DOM Update (UI)
```

## 🚀 Key Features

### Modular Architecture
- Separated concerns (HTML/CSS/JS)
- Reusable components
- Easy to maintain and extend

### Professional UI/UX
- Sidebar navigation
- Top bar with user info
- Responsive design
- Smooth animations
- Clean, modern aesthetics

### Scalable Codebase
- Module pattern in JavaScript
- CSS variables for theming
- RESTful API design
- Database normalization

## 📝 Best Practices

### Code Organization
✅ Separate files for HTML, CSS, JS
✅ Modular JavaScript with clear responsibilities
✅ CSS variables for consistent theming
✅ Semantic HTML5 elements

### Performance
✅ Efficient DOM updates
✅ Debounced API calls
✅ Lazy loading where applicable
✅ Optimized animations

### Maintainability
✅ Clear naming conventions
✅ Comprehensive comments
✅ Consistent code style
✅ Version control friendly

### Security
✅ Input validation
✅ SQL injection prevention (ORM)
✅ XSS protection
✅ CSRF tokens (Flask)

## 🔧 Development Workflow

1. **Backend Development**: Modify `app.py` or `database.py`
2. **Frontend Styling**: Edit `static/css/admin.css`
3. **Frontend Logic**: Update `static/js/admin.js`
4. **UI Structure**: Modify `templates/admin.html`
5. **Testing**: Test in browser, check console for errors
6. **Database Changes**: Run `migrate_database.py`

## 📚 Documentation

- **README.md**: General project information
- **MIGRATION.md**: Database migration guide
- **CHANGELOG.md**: Version history
- **PROJECT_STRUCTURE.md**: This file

## 🎨 Design System

### Colors
- Primary: #3498db (Blue)
- Success: #2ecc71 (Green)
- Danger: #e74c3c (Red)
- Warning: #f39c12 (Orange)
- Dark: #2c3e50

### Typography
- Font Family: Inter, system fonts
- Headings: 700-800 weight
- Body: 400-600 weight

### Spacing
- Base unit: 8px
- Small: 0.5rem (8px)
- Medium: 1rem (16px)
- Large: 1.5rem (24px)

### Shadows
- Small: 0 2px 8px rgba(0,0,0,0.08)
- Medium: 0 4px 15px rgba(0,0,0,0.1)
- Large: 0 8px 25px rgba(0,0,0,0.15)

## 🔐 Security Considerations

- User authentication (to be implemented)
- API rate limiting (to be implemented)
- Input sanitization (implemented)
- Secure file uploads (implemented)
- Database encryption (optional)

## 🚀 Future Enhancements

- [ ] User authentication & authorization
- [ ] Real-time WebSocket updates
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Export/import configurations
- [ ] Automated backups
- [ ] Email notifications
- [ ] Mobile app

## 📞 Support

For issues or questions:
1. Check documentation
2. Review code comments
3. Check console for errors
4. Review API responses

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Maintainer**: StreamLive Team
