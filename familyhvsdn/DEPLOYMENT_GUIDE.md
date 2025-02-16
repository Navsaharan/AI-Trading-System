# FamilyHVSDN - Deployment Guide

## Local Development Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/familyhvsdn.git
cd familyhvsdn
```

2. **Set Up Python Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set Up Environment Variables**
Create a `.env` file in the root directory:
```env
FLASK_APP=src/app.py
FLASK_ENV=production
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url
```

## Server Deployment

### Option 1: Deploy on Ubuntu Server

1. **Server Prerequisites**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx redis-server
```

2. **Clone and Setup Project**
```bash
cd /var/www
git clone https://github.com/yourusername/familyhvsdn.git
cd familyhvsdn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure Nginx**
Create `/etc/nginx/sites-available/familyhvsdn`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/familyhvsdn/src/frontend/static;
    }

    location /socket.io {
        proxy_pass http://localhost:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

4. **Enable the Site**
```bash
sudo ln -s /etc/nginx/sites-available/familyhvsdn /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

5. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

6. **Create Systemd Service**
Create `/etc/systemd/system/familyhvsdn.service`:
```ini
[Unit]
Description=FamilyHVSDN Trading System
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/familyhvsdn
Environment="PATH=/var/www/familyhvsdn/venv/bin"
ExecStart=/var/www/familyhvsdn/venv/bin/python src/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Start the Service**
```bash
sudo systemctl start familyhvsdn
sudo systemctl enable familyhvsdn
```

### Option 2: Deploy on Heroku

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login and Create App**
```bash
heroku login
heroku create familyhvsdn
```

3. **Add Buildpacks**
```bash
heroku buildpacks:add heroku/python
```

4. **Configure Environment Variables**
```bash
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-database-url
heroku config:set REDIS_URL=your-redis-url
```

5. **Deploy**
```bash
git push heroku main
```

### Option 3: Deploy on AWS

1. **Create EC2 Instance**
- Launch Ubuntu Server 20.04 LTS instance
- Configure Security Groups (ports 80, 443, 22)
- Create and download key pair

2. **Connect to Instance**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Follow Ubuntu Server deployment steps above**

## Domain Configuration

1. **Purchase Domain**
- Purchase domain from registrar (e.g., GoDaddy, Namecheap)

2. **Configure DNS**
- Add A record pointing to your server IP
- Add CNAME record for www subdomain

3. **Wait for DNS Propagation**
- Can take up to 48 hours
- Check propagation status at whatsmydns.net

## Monitoring and Maintenance

1. **Setup Monitoring**
```bash
sudo apt install prometheus node-exporter
pip install prometheus-client
```

2. **Regular Maintenance**
```bash
# Update system
sudo apt update && sudo apt upgrade

# Update Python packages
pip install -r requirements.txt --upgrade

# Backup database
pg_dump -U username database_name > backup.sql

# Check logs
sudo journalctl -u familyhvsdn
```

## Security Considerations

1. **Firewall Configuration**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

2. **Regular Updates**
```bash
# Security updates
sudo unattended-upgrades
```

3. **SSL Certificate Renewal**
```bash
sudo certbot renew
```

## Troubleshooting

1. **Check Application Logs**
```bash
sudo journalctl -u familyhvsdn -f
```

2. **Check Nginx Logs**
```bash
sudo tail -f /var/log/nginx/error.log
```

3. **Check System Resources**
```bash
htop
df -h
free -m
```

## Backup and Recovery

1. **Database Backup**
```bash
# Backup
pg_dump -U username database_name > backup.sql

# Restore
psql -U username database_name < backup.sql
```

2. **File Backup**
```bash
# Backup application files
tar -czf backup.tar.gz /var/www/familyhvsdn

# Backup to S3 (if using AWS)
aws s3 cp backup.tar.gz s3://your-bucket/
```

## Performance Optimization

1. **Enable Caching**
```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo systemctl enable redis-server
```

2. **Configure Nginx Caching**
Add to Nginx configuration:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m use_temp_path=off;
```

## Contact and Support

For support:
- Email: support@your-domain.com
- Phone: Your-Support-Number
- Working Hours: 9 AM - 6 PM IST
