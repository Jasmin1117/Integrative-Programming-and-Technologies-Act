# 🚀 Contabo VPS10 Deployment Guide for Django Project
## Complete Production Deployment with Security & VS Code Remote Development

This comprehensive guide will walk you through deploying your Django project on a **Contabo VPS10** server with enterprise-grade security measures and VS Code remote development capabilities.

---

## 📋 Table of Contents
1. [Prerequisites & Server Selection](#prerequisites--server-selection)
2. [Initial Server Setup & Security Hardening](#initial-server-setup--security-hardening)
3. [VS Code Remote Development Setup](#vs-code-remote-development-setup)
4. [Django Project Deployment](#django-project-deployment)
5. [Production Security Measures](#production-security-measures)
6. [SSL/HTTPS Configuration](#sslhttps-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites & Server Selection

### Contabo VPS10 Specifications
- **CPU**: 4 vCores
- **RAM**: 8 GB
- **Storage**: 200 GB NVMe SSD
- **Bandwidth**: 32 TB
- **Price**: ~€8.99/month
- **OS**: Ubuntu 22.04 LTS (Recommended)

### What You'll Need
- ✅ Contabo VPS10 server
- ✅ Domain name (optional but recommended)
- ✅ SSH access to your server
- ✅ VS Code with Remote Development extension
- ✅ Basic Linux command line knowledge

---

## 🔒 Initial Server Setup & Security Hardening

### Step 1: Initial Server Access
```bash
# Connect to your server as root
ssh root@YOUR_SERVER_IP

# Update system packages
apt update && apt upgrade -y
apt install -y curl wget htop nano vim ufw fail2ban
```

### Step 2: Create Secure Non-Root User
```bash
# Create django user with sudo privileges
adduser django
usermod -aG sudo django

# Set up SSH key authentication (DO NOT use password auth)
mkdir -p /home/django/.ssh
chmod 700 /home/django/.ssh
```

### Step 3: SSH Security Hardening
```bash
# Edit SSH configuration
nano /etc/ssh/sshd_config
```

**Add/Modify these security settings:**
```bash
# Disable root login
PermitRootLogin no

# Disable password authentication
PasswordAuthentication no

# Use key-based authentication only
PubkeyAuthentication yes

# Change default SSH port (optional but recommended)
Port 2222

# Limit SSH attempts
MaxAuthTries 3

# Set idle timeout
ClientAliveInterval 300
ClientAliveCountMax 2

# Restrict users who can SSH
AllowUsers django

# Disable empty passwords
PermitEmptyPasswords no
```

**Restart SSH service:**
```bash
systemctl restart sshd
systemctl enable sshd

# Test new SSH connection before closing current session
ssh -p 2222 django@YOUR_SERVER_IP
```

### Step 4: Firewall Configuration (UFW)
```bash
# Configure UFW firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 2222/tcp  # SSH (if you changed port)
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 22/tcp    # SSH (if keeping default port)
ufw enable

# Check firewall status
ufw status verbose
```

### Step 5: Fail2Ban Setup
```bash
# Configure Fail2Ban for SSH protection
nano /etc/fail2ban/jail.local
```

**Add this configuration:**
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 2222  # or 22 if you kept default
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
```

**Enable and start Fail2Ban:**
```bash
systemctl enable fail2ban
systemctl start fail2ban
fail2ban-client status
```

---

## 💻 VS Code Remote Development Setup

### Step 1: Install VS Code Remote Development Extension
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Remote - SSH"
4. Install the extension

### Step 2: Configure SSH Config
**On your local machine, edit `~/.ssh/config`:**
```bash
nano ~/.ssh/config
```

**Add your server configuration:**
```bash
Host contabo-vps10
    HostName YOUR_SERVER_IP
    User django
    Port 2222  # or 22 if you kept default
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Step 3: Connect to Remote Server
1. In VS Code, press `Ctrl+Shift+P`
2. Type "Remote-SSH: Connect to Host"
3. Select "contabo-vps10"
4. Choose "Linux" when prompted
5. Wait for connection to establish

### Step 4: Open Project Folder
1. Once connected, click "Open Folder"
2. Navigate to `/home/django/connectly_project`
3. Open the project folder

---

## 🚀 Django Project Deployment

### Step 1: Install System Dependencies
```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install web server and database
sudo apt install -y nginx postgresql postgresql-contrib

# Install Node.js for Tailwind CSS
sudo apt install -y nodejs npm

# Install additional dependencies
sudo apt install -y git curl wget unzip

# Install SSL certificate tools
sudo apt install -y certbot python3-certbot-nginx

# Install system libraries for Python packages
sudo apt install -y libpq-dev libjpeg-dev libpng-dev libfreetype6-dev
sudo apt install -y build-essential libssl-dev libffi-dev
```

### Step 2: PostgreSQL Database Setup
```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

**In PostgreSQL prompt:**
```sql
CREATE DATABASE connectly_db;
CREATE USER connectly_user WITH PASSWORD 'YOUR_SUPER_SECURE_PASSWORD_123!@#';
GRANT ALL PRIVILEGES ON DATABASE connectly_db TO connectly_user;
ALTER USER connectly_user CREATEDB;
\q
```

**Test database connection:**
```bash
sudo -u postgres psql -d connectly_db -U connectly_user -h localhost
```

### Step 3: Clone and Setup Project
```bash
# Navigate to home directory
cd /home/django

# Clone your project (replace with your actual repository)
git clone https://github.com/YOUR_USERNAME/connectly_project.git
cd connectly_project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn psycopg2-binary
```

### Step 4: Environment Configuration
```bash
# Create production environment file
nano .env
```

**Add your production environment variables:**
```bash
DEBUG=False
SECRET_KEY=your_super_secure_secret_key_here
DATABASE_URL=postgresql://connectly_user:YOUR_SUPER_SECURE_PASSWORD_123!@#@localhost/connectly_db
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_SERVER_IP
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Step 5: Django Production Settings
**Create `connectly_project/settings_production.py`:**
```python
from .settings import *
import os

# Security Settings
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'connectly_db',
        'USER': 'connectly_user',
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Static Files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media Files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/connectly.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Step 6: Database Migration
```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test the application
python manage.py runserver 0.0.0.0:8000
```

---

## 🛡️ Production Security Measures

### Step 1: Gunicorn Configuration
**Create `gunicorn.conf.py`:**
```python
# Gunicorn configuration file
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### Step 2: Systemd Service Configuration
**Create `/etc/systemd/system/connectly.service`:**
```ini
[Unit]
Description=Connectly Django Application
After=network.target

[Service]
User=django
Group=django
WorkingDirectory=/home/django/connectly_project
Environment="PATH=/home/django/connectly_project/venv/bin"
ExecStart=/home/django/connectly_project/venv/bin/gunicorn --config gunicorn.conf.py connectly_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable connectly
sudo systemctl start connectly
sudo systemctl status connectly
```

### Step 3: Nginx Configuration
**Create `/etc/nginx/sites-available/connectly`:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Static Files
    location /static/ {
        alias /home/django/connectly_project/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /home/django/connectly_project/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }

    location ~ ~$ {
        deny all;
    }
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/connectly /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 SSL/HTTPS Configuration

### Step 1: Domain DNS Configuration
1. Point your domain's A record to your server IP
2. Wait for DNS propagation (can take up to 48 hours)

### Step 2: Let's Encrypt SSL Certificate
```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Start Nginx
sudo systemctl start nginx

# Test SSL configuration
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Auto-renewal Setup
```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Add to crontab for automatic renewal
sudo crontab -e
```

**Add this line:**
```bash
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Monitoring & Maintenance

### Step 1: Log Monitoring
```bash
# Create log directory
sudo mkdir -p /var/log/django
sudo chown django:django /var/log/django

# Monitor logs in real-time
sudo tail -f /var/log/django/connectly.log
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Step 2: System Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor system resources
htop
iotop
nethogs
```

### Step 3: Backup Strategy
**Create backup script `/home/django/backup.sh`:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/django/backups"
PROJECT_DIR="/home/django/connectly_project"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump connectly_db > $BACKUP_DIR/db_backup_$DATE.sql

# Project files backup
tar -czf $BACKUP_DIR/project_backup_$DATE.tar.gz $PROJECT_DIR

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Make it executable and add to crontab:**
```bash
chmod +x /home/django/backup.sh
crontab -e
```

**Add this line for daily backups at 2 AM:**
```bash
0 2 * * * /home/django/backup.sh
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Django Service Won't Start
```bash
# Check service status
sudo systemctl status connectly

# Check logs
sudo journalctl -u connectly -f

# Check file permissions
sudo chown -R django:django /home/django/connectly_project
```

#### 2. Nginx Configuration Errors
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### 3. Database Connection Issues
```bash
# Test PostgreSQL connection
sudo -u postgres psql -d connectly_db -U connectly_user -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### 4. SSL Certificate Issues
```bash
# Check certificate validity
sudo certbot certificates

# Renew certificate manually
sudo certbot renew
```

---

## 🎉 Deployment Complete!

Your Django project is now deployed on Contabo VPS10 with:
- ✅ Enterprise-grade security measures
- ✅ SSL/HTTPS encryption
- ✅ VS Code remote development capability
- ✅ Automated backups
- ✅ Monitoring and logging
- ✅ Production-ready configuration

### Next Steps:
1. **Test your application** at `https://yourdomain.com`
2. **Set up monitoring alerts** for uptime
3. **Configure regular security updates**
4. **Monitor performance metrics**
5. **Set up CI/CD pipeline** (optional)

### Security Checklist:
- [ ] SSH key authentication only
- [ ] Firewall configured (UFW)
- [ ] Fail2Ban active
- [ ] Non-root user with sudo
- [ ] SSL certificate installed
- [ ] Security headers configured
- [ ] Regular backups scheduled
- [ ] System updates automated

---

## 📚 Additional Resources

- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [Nginx Security Configuration](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [Ubuntu Server Security Guide](https://ubuntu.com/server/docs)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**Happy Deploying! 🚀**

*For support, check the troubleshooting section or refer to the official documentation of the tools used.*
