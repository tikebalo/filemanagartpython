# 🚀 FileManager Pro

<div align="center">

![FileManager Pro](https://img.shields.io/badge/FileManager-Pro-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)
![License](https://img.shields.io/badge/License-MIT-yellow)

Full-featured file manager with cloud storage capabilities, conversion tools, and download utilities.

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API](#-api-documentation)

</div>

---

## 📋 Features

### Core File Management
- ✅ **File Operations**: Upload, download, rename, move, copy, delete
- ✅ **Folder Management**: Create, navigate, tree view
- ✅ **Multiple Views**: Grid and list view with customizable icon sizes
- ✅ **Search**: Powerful search with recursive directory scanning
- ✅ **Sorting & Filtering**: Sort by name, size, date; filter by file type
- ✅ **Favorites**: Quick access to frequently used files
- ✅ **Trash**: 30-day retention with restore functionality

### Advanced Features
- 🔗 **Public Share Links**: Password-protected, expiring links with download limits
- 🔄 **File Conversion**: Audio (mp3, wav, flac) and image (jpeg, png, webp) conversion
- 📥 **Downloaders**: YouTube and direct URL downloads
- 🗜️ **Archive Management**: Create and extract ZIP, TAR archives
- 📊 **Admin Dashboard**: User management, storage statistics, activity logs
- 🔔 **Real-time Updates**: WebSocket notifications for file changes

### User Experience
- 🎨 **Themes**: Light and dark mode with 6 accent colors
- 🌐 **i18n**: Multi-language support (English, Russian)
- ⌨️ **Keyboard Shortcuts**: Ctrl+C/V, Delete, F2, and more
- 📱 **PWA Ready**: Install as a desktop/mobile app
- 🔐 **Secure**: JWT authentication, role-based access control

---

## 🚀 Quick Start

### Using Docker (Recommended)

\`\`\`bash
# Clone repository
git clone https://github.com/yourusername/filemanager.git
cd filemanager

# Create environment file
cp .env.example .env

# Start services
docker-compose up -d

# Create admin user (first time only)
docker-compose exec backend python -c "
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.utils.security import hash_password
Base.metadata.create_all(bind=engine)
db = SessionLocal()
admin = User(username='admin', password_hash=hash_password('admin'), role='admin', quota=0)
db.add(admin)
db.commit()
print('✅ Admin user created: admin/admin')
"
\`\`\`

**Access the application:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📖 API Docs: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

\`\`\`bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload
\`\`\`

#### Frontend Setup

\`\`\`bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
\`\`\`

---

## 📁 Project Structure

\`\`\`
filemanager/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── utils/             # Utilities
│   │   └── main.py            # FastAPI app
│   └── storage/               # File storage
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── api/               # API clients
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── store/             # Zustand stores
│   └── public/
│
├── docker-compose.yml
├── Makefile
└── README.md
\`\`\`

---

## 🔧 Configuration

### Environment Variables

Create \`.env\` file:

\`\`\`env
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./storage/database.db
STORAGE_PATH=./storage
CORS_ORIGINS=http://localhost:3000
\`\`\`

### Default Credentials

\`\`\`
Username: admin
Password: admin
\`\`\`

**⚠️ Change after first login!**

---

## 📖 API Documentation

Full interactive API documentation: http://localhost:8000/docs

### Quick Examples

**Login:**
\`\`\`bash
curl -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"admin"}'
\`\`\`

**List Files:**
\`\`\`bash
curl http://localhost:8000/api/files/?path=/ \\
  -H "Authorization: Bearer YOUR_TOKEN"
\`\`\`

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+C | Copy |
| Ctrl+X | Cut |
| Ctrl+V | Paste |
| Ctrl+A | Select all |
| Delete | Move to trash |
| F2 | Rename |
| Ctrl+F | Search |
| Escape | Clear selection |

---

## 🐳 Docker Commands

\`\`\`bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose build --no-cache
\`\`\`

---

## 🛠️ Makefile Commands

\`\`\`bash
make install    # Install dependencies
make dev        # Run development servers
make build      # Build Docker images
make up         # Start containers
make down       # Stop containers
make logs       # View logs
make clean      # Clean up
\`\`\`

---

## 🔒 Security Features

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting
- ✅ Path traversal protection
- ✅ File type validation
- ✅ CORS configuration
- ✅ Security headers

---

## 🐛 Troubleshooting

### Large file uploads fail
Increase nginx \`client_max_body_size\`:
\`\`\`nginx
client_max_body_size 5G;
\`\`\`

### YouTube downloads fail
Update yt-dlp:
\`\`\`bash
pip install -U yt-dlp
\`\`\`

### Database locked
Use PostgreSQL for production:
\`\`\`env
DATABASE_URL=postgresql://user:pass@localhost/filemanager
\`\`\`

---

## 📝 TODO

- [ ] Drag & drop upload
- [ ] File preview
- [ ] Bulk operations
- [ ] File versioning
- [ ] Mobile app

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 👨‍💻 Author

**Chmo228**

---

<div align="center">

**Made with ❤️**

⭐ Star this repo if helpful!

</div>
