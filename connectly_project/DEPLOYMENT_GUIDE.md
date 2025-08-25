# Django Project Deployment Guide for Contabo VPS10

This guide will walk you through deploying your Django project on a Contabo VPS10 server step by step.

## Prerequisites

- Contabo VPS10 server with Ubuntu 22.04 LTS
- Domain name (optional but recommended)
- SSH access to your server
- Basic Linux command line knowledge

## Step 1: Server Setup and Security

### 1.1 Connect to Your Server
```bash
ssh root@YOUR_SERVER_IP
```

### 1.2 Update System
```bash
apt update && apt upgrade -y
```

### 1.3 Create a Non-Root User
```bash
adduser django
usermod -aG sudo django
```

### 1.4 Set Up SSH Key Authentication
```bash
# On your local machine, generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096

# Copy your public key to the server
ssh-copy-id django@YOUR_SERVER_IP

# Test the new user
ssh django@YOUR_SERVER_IP
```

### 1.5 Configure Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Step 2: Install Required Software

### 2.1 Install Python and Dependencies
```bash
sudo apt install python3 python3-pip python3-venv python3-dev -y
sudo apt install nginx -y
sudo apt install postgresql postgresql-contrib -y
sudo apt install nodejs npm -y
sudo apt install git -y
sudo apt install certbot python3-certbot-nginx -y
```

### 2.2 Install System Dependencies for Python Packages
```bash
sudo apt install libpq-dev libjpeg-dev libpng-dev libfreetype6-dev -y
sudo apt install build-essential libssl-dev libffi-dev -y
```

## Step 3: Database Setup

### 3.1 Configure PostgreSQL
```bash
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE connectly_db;
CREATE USER connectly_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE connectly_db TO connectly_user;
ALTER USER connectly_user CREATEDB;
\q
```

### 3.2 Test Database Connection
```bash
sudo -u postgres psql -d connectly_db -U connectly_user -h localhost
```

## Step 4: Project Deployment

### 4.1 Clone Your Project
```bash
cd /home/django
git clone YOUR_GIT_REPOSITORY_URL connectly_project
cd connectly_project
```

### 4.2 Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4.3 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Install Tailwind CSS
```bash
cd theme/static_src
npm install
npm run build
cd ../..
```

## Step 5: Environment Configuration

### 5.1 Create Environment File
```bash
nano .env
```

Add the following content:
```env
DEBUG=False
SECRET_KEY=YOUR_NEW_SECRET_KEY_HERE
DATABASE_URL=postgresql://connectly_user:YOUR_SECURE_PASSWORD@localhost/connectly_db
GOOGLE_OAUTH_CLIENT_ID=YOUR_GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET=YOUR_GOOGLE_OAUTH_CLIENT_SECRET
ALLOWED_HOSTS=YOUR_DOMAIN_OR_IP,www.YOUR_DOMAIN_OR_IP
CSRF_TRUSTED_ORIGINS=https://YOUR_DOMAIN_OR_IP,https://www.YOUR_DOMAIN_OR_IP
```

### 5.2 Generate New Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 6: Django Configuration Updates

### 6.1 Update Settings for Production
```bash
nano connectly_project/settings.py
```

Update these settings:
```python
DEBUG = False
ALLOWED_HOSTS = ['YOUR_DOMAIN_OR_IP', 'www.YOUR_DOMAIN_OR_IP', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'connectly_db',
        'USER': 'connectly_user',
        'PASSWORD': 'YOUR_SECURE_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Enable SSL settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 6.2 Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6.3 Run Migrations
```bash
python manage.py migrate
```

### 6.4 Create Superuser
```bash
python manage.py createsuperuser
```

## Step 7: Gunicorn Configuration

### 7.1 Install Gunicorn
```bash
pip install gunicorn
```

### 7.2 Create Gunicorn Service File
```bash
sudo nano /etc/systemd/system/connectly.service
```

Add this content:
```ini
[Unit]
Description=Connectly Django Application
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/connectly_project
Environment="PATH=/home/django/connectly_project/venv/bin"
ExecStart=/home/django/connectly_project/venv/bin/gunicorn --workers 3 --bind unix:/home/django/connectly_project/connectly.sock connectly_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 7.3 Start and Enable Gunicorn Service
```bash
sudo systemctl start connectly
sudo systemctl enable connectly
sudo systemctl status connectly
```

## Step 8: Nginx Configuration

### 8.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/connectly
```

Add this content:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP www.YOUR_DOMAIN_OR_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/django/connectly_project;
    }
    
    location /media/ {
        root /home/django/connectly_project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/connectly_project/connectly.sock;
    }
}
```

### 8.2 Enable the Site
```bash
sudo ln -s /etc/nginx/sites-available/connectly /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Step 9: SSL Certificate (Optional but Recommended)

### 9.1 Install SSL Certificate
```bash
sudo certbot --nginx -d YOUR_DOMAIN_OR_IP -d www.YOUR_DOMAIN_OR_IP
```

### 9.2 Auto-renewal
```bash
sudo crontab -e
```

Add this line:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## Step 10: Final Configuration and Testing

### 10.1 Set Proper Permissions
```bash
sudo chown -R django:www-data /home/django/connectly_project
sudo chmod -R 755 /home/django/connectly_project
```

### 10.2 Test the Application
```bash
# Check if all services are running
sudo systemctl status nginx
sudo systemctl status connectly
sudo systemctl status postgresql

# Test the website
curl -I http://YOUR_DOMAIN_OR_IP
```

### 10.3 Monitor Logs
```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Gunicorn logs
sudo journalctl -u connectly -f
```

## Step 11: Maintenance and Updates

### 11.1 Update Application
```bash
cd /home/django/connectly_project
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart connectly
```

### 11.2 Backup Database
```bash
sudo -u postgres pg_dump connectly_db > /home/django/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 11.3 Monitor System Resources
```bash
htop
df -h
free -h
```

## Troubleshooting

### Common Issues and Solutions

1. **Permission Denied Errors**
   ```bash
   sudo chown -R django:www-data /home/django/connectly_project
   sudo chmod -R 755 /home/django/connectly_project
   ```

2. **Database Connection Issues**
   ```bash
   sudo systemctl status postgresql
   sudo -u postgres psql -d connectly_db
   ```

3. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --noinput
   sudo systemctl restart nginx
   ```

4. **Gunicorn Service Issues**
   ```bash
   sudo systemctl status connectly
   sudo journalctl -u connectly -f
   ```

## Security Checklist

- [ ] Firewall configured (UFW)
- [ ] Non-root user created
- [ ] SSH key authentication enabled
- [ ] Database user with limited privileges
- [ ] SSL certificate installed
- [ ] Django DEBUG set to False
- [ ] Secret key changed from default
- [ ] Allowed hosts configured
- [ ] CSRF trusted origins set
- [ ] Static files collected
- [ ] Media files permissions set

## Performance Optimization

1. **Enable Gzip Compression in Nginx**
2. **Configure Browser Caching**
3. **Use CDN for Static Files**
4. **Database Query Optimization**
5. **Redis for Caching (Optional)**

## Backup Strategy

1. **Daily Database Backups**
2. **Weekly Full System Backups**
3. **Code Repository Backups**
4. **Environment Configuration Backups**

---

**Note**: Replace `YOUR_DOMAIN_OR_IP`, `YOUR_SECURE_PASSWORD`, and other placeholder values with your actual configuration values.

**Support**: If you encounter issues, check the logs mentioned in Step 10.3 and refer to the troubleshooting section.
