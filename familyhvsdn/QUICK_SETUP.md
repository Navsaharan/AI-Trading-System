# FamilyHVSDN - Quick Setup Guide

## 1. Local Development

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- Redis Server
- PostgreSQL

### Setup Steps

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/familyhvsdn.git
cd familyhvsdn
```

2. **Install Python Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install Node.js Dependencies**
```bash
cd src/frontend
npm install
```

4. **Set Up Environment Variables**
Create `.env` file in root directory:
```env
FLASK_APP=src/app.py
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://username:password@localhost/familyhvsdn
REDIS_URL=redis://localhost:6379
```

5. **Initialize Database**
```bash
flask db upgrade
```

6. **Run Development Servers**
```bash
# Terminal 1 - Backend
python src/app.py

# Terminal 2 - Frontend (Hot Reload)
cd src/frontend
npm start
```

7. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Admin Dashboard: http://localhost:3000/admin

## 2. File Structure

```
familyhvsdn/
├── src/
│   ├── frontend/
│   │   ├── public/
│   │   ├── static/
│   │   └── templates/
│   ├── ai/
│   ├── services/
│   ├── routes/
│   └── app.py
├── tests/
├── requirements.txt
├── package.json
└── README.md
```

## 3. Available Scripts

```bash
# Run tests
python -m pytest

# Run linting
flake8 src/

# Format code
black src/

# Create database migrations
flask db migrate -m "Migration message"

# Apply database migrations
flask db upgrade
```

## 4. Common Issues

1. **Database Connection Error**
```bash
# Check PostgreSQL service
sudo service postgresql status

# Create database
createdb familyhvsdn
```

2. **Redis Connection Error**
```bash
# Check Redis service
sudo service redis-server status

# Clear Redis cache
redis-cli flushall
```

3. **Node Modules Issues**
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

## 5. Useful Commands

```bash
# Create admin user
flask create-admin

# Backup database
pg_dump -U username familyhvsdn > backup.sql

# Restore database
psql -U username familyhvsdn < backup.sql

# Check logs
tail -f logs/app.log
```

For detailed deployment instructions, see DEPLOYMENT_GUIDE.md
