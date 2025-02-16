# FamilyHVSDN - Complete Trading System Setup Guide

## Project Overview

FamilyHVSDN is an advanced Indian trading system that combines real-time market data with AI-powered predictions. 

### Key Features

1. **Real-time Market Data**
   - Live stock prices from NSE/BSE
   - Technical indicators (SMA, RSI, MACD)
   - Volume analysis
   - Market depth

2. **AI Predictions**
   - Price predictions using LSTM
   - Sentiment analysis of news
   - Market regime detection
   - Risk analysis

3. **User Features**
   - Portfolio tracking
   - Real-time alerts
   - Custom watchlists
   - Performance analytics
   - Mobile-responsive interface

4. **Admin Features**
   - User management
   - System monitoring
   - Risk management
   - Performance tracking
   - API key management

## Complete Setup Guide

### 1. System Requirements

```bash
# Ubuntu 20.04 or higher
sudo apt update
sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.8 python3-pip nodejs npm redis-server postgresql nginx

# Install Python virtual environment
sudo apt install -y python3.8-venv

# Install Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 16
nvm use 16
```

### 2. Project Setup

```bash
# Clone repository
git clone https://github.com/yourusername/familyhvsdn.git
cd familyhvsdn

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Create necessary directories
mkdir -p training_data/{stocks,indices,news,processed}
mkdir -p ai_models
mkdir -p logs
```

### 3. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE familyhvsdn;
CREATE USER familyhvsdn_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE familyhvsdn TO familyhvsdn_user;
\q

# Run database migrations
flask db upgrade
```

### 4. Environment Configuration

Create `.env` file:
```bash
# Application
FLASK_APP=src/app.py
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=postgresql://familyhvsdn_user:your_password@localhost/familyhvsdn
REDIS_URL=redis://localhost:6379/0

# APIs
ZERODHA_API_KEY=your-zerodha-key
ZERODHA_API_SECRET=your-zerodha-secret
UPSTOX_API_KEY=your-upstox-key
UPSTOX_API_SECRET=your-upstox-secret

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 5. Broker API Integration

1. **Zerodha Integration:**
```python
# In src/brokers/zerodha.py
from kiteconnect import KiteConnect

kite = KiteConnect(api_key=os.getenv('ZERODHA_API_KEY'))
```

2. **Upstox Integration:**
```python
# In src/brokers/upstox.py
from upstox_api.api import Upstox

upstox = Upstox(os.getenv('UPSTOX_API_KEY'))
```

### 6. Server Deployment

#### A. Using Ubuntu Server

1. **Configure Nginx:**
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/familyhvsdn

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/familyhvsdn/static;
    }

    location /socket.io {
        proxy_pass http://localhost:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}

# Enable the site
sudo ln -s /etc/nginx/sites-available/familyhvsdn /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

2. **Setup SSL:**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

3. **Create Systemd Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/familyhvsdn.service

# Add configuration:
[Unit]
Description=FamilyHVSDN Trading System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/familyhvsdn
Environment="PATH=/path/to/familyhvsdn/venv/bin"
ExecStart=/path/to/familyhvsdn/venv/bin/gunicorn -w 4 -k gevent -b 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target

# Start service
sudo systemctl start familyhvsdn
sudo systemctl enable familyhvsdn
```

### 7. Starting the System

```bash
# 1. Start all services
sudo systemctl start redis-server
sudo systemctl start postgresql
sudo systemctl start nginx
sudo systemctl start familyhvsdn

# 2. Start the application
python start.py
```

### 8. User Roles and Permissions

1. **Admin Capabilities:**
   - User management
   - System configuration
   - Risk management
   - API key management
   - Performance monitoring

2. **User Capabilities:**
   - Portfolio management
   - Trading execution
   - Watchlist creation
   - Alert setup
   - Performance tracking

### 9. Common Tasks

1. **Create Admin User:**
```bash
python manage.py create-admin
```

2. **Backup Database:**
```bash
pg_dump -U familyhvsdn_user familyhvsdn > backup.sql
```

3. **Update System:**
```bash
git pull
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart familyhvsdn
```

### 10. Monitoring and Maintenance

1. **View Logs:**
```bash
# Application logs
tail -f logs/app.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u familyhvsdn
```

2. **Monitor Resources:**
```bash
# System resources
htop

# Disk usage
df -h

# Memory usage
free -m
```

### 11. Troubleshooting

1. **Application Issues:**
   - Check application logs: `tail -f logs/app.log`
   - Verify database connection
   - Check API credentials

2. **Data Collection Issues:**
   - Check internet connection
   - Verify API access
   - Check disk space

3. **Model Issues:**
   - Check GPU availability
   - Verify model files
   - Check training logs

### 12. Security Best Practices

1. **Server Security:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# Secure PostgreSQL
sudo nano /etc/postgresql/12/main/pg_hba.conf
```

2. **Application Security:**
   - Use strong passwords
   - Enable 2FA
   - Regular backups
   - Monitor access logs

### 13. Scaling the System

1. **Horizontal Scaling:**
   - Add more application servers
   - Load balance with Nginx
   - Replicate database

2. **Vertical Scaling:**
   - Increase server resources
   - Optimize database
   - Cache frequently accessed data

### Need Help?

- Technical Support: support@your-domain.com
- Trading Support: trading@your-domain.com
- Emergency: emergency@your-domain.com

### Additional Resources

1. Documentation: `docs/`
2. API Documentation: `docs/API.md`
3. User Guide: `docs/USER_GUIDE.md`
4. Admin Guide: `docs/ADMIN_GUIDE.md`
