# 🚀 Contabo VPS10 Deployment Quick Reference
## Essential Commands and Steps for Quick Deployment

---

## 📋 Pre-Deployment Checklist

- [ ] Contabo VPS10 server running Ubuntu 22.04 LTS
- [ ] SSH access configured with key authentication
- [ ] Domain name pointing to server IP (optional)
- [ ] VS Code with Remote-SSH extension installed

---

## 🔑 Initial Server Setup

### Connect and Update
```bash
# Connect to server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y
```

### Create Django User
```bash
# Create user
adduser django
usermod -aG sudo django

# Setup SSH for django user
mkdir -p /home/django/.ssh
chmod 700 /home/django/.ssh
```

### Security Hardening
```bash
# SSH security
nano /etc/ssh/sshd_config
# Set: PermitRootLogin no, PasswordAuthentication no

# Restart SSH
systemctl restart sshd

# Firewall
ufw default deny incoming
ufw allow 22,80,443
ufw enable

# Fail2Ban
apt install fail2ban
systemctl enable fail2ban
```

---

## 🚀 Automated Deployment

### Run Deployment Script
```bash
# Switch to django user
su - django

# Make script executable
chmod +x deploy_production.sh

# Run deployment
./deploy_production.sh
```

### Manual Deployment Steps
```bash
# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql

# Setup database
sudo -u postgres psql
CREATE DATABASE connectly_db;
CREATE USER connectly_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE connectly_db TO connectly_user;
\q

# Setup project
cd /home/django
git clone YOUR_REPO connectly_project
cd connectly_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_production.txt
```

---

## ⚙️ Service Configuration

### Gunicorn Service
```bash
# Check status
sudo systemctl status connectly

# Start/Stop/Restart
sudo systemctl start connectly
sudo systemctl stop connectly
sudo systemctl restart connectly

# View logs
sudo journalctl -u connectly -f
```

### Nginx Configuration
```bash
# Test config
sudo nginx -t

# Reload/Restart
sudo systemctl reload nginx
sudo systemctl restart nginx

# View logs
sudo tail -f /var/log/nginx/error.log
```

### PostgreSQL Service
```bash
# Check status
sudo systemctl status postgresql

# Start/Stop
sudo systemctl start postgresql
sudo systemctl stop postgresql
```

---

## 🔐 SSL Certificate Setup

### Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run

# Add to crontab
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 💻 VS Code Remote Setup

### SSH Configuration
```bash
# Local machine: ~/.ssh/config
Host contabo-vps10
    HostName YOUR_SERVER_IP
    User django
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

### Connect in VS Code
1. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
2. Select "contabo-vps10"
3. Open folder: `/home/django/connectly_project`

---

## 🔧 Common Commands

### Django Management
```bash
# Activate environment
source venv/bin/activate

# Run server
python manage.py runserver 0.0.0.0:8000

# Migrations
python manage.py makemigrations
python manage.py migrate

# Static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser
```

### System Monitoring
```bash
# Resource usage
htop
df -h
free -h

# Service status
sudo systemctl status connectly nginx postgresql

# Network
sudo netstat -tlnp
sudo ufw status
```

### Logs and Debugging
```bash
# Django logs
sudo tail -f /var/log/django/connectly.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u connectly -f
```

---

## 🛡️ Security Commands

### Firewall Management
```bash
# Check status
sudo ufw status verbose

# Allow/Deny ports
sudo ufw allow 22/tcp
sudo ufw deny 3306/tcp

# Reset firewall
sudo ufw reset
```

### Fail2Ban Management
```bash
# Check status
sudo fail2ban-client status

# Check specific jail
sudo fail2ban-client status sshd

# Unban IP
sudo fail2ban-client set sshd unbanip IP_ADDRESS
```

### SSH Security
```bash
# Check SSH config
sudo nano /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart sshd

# Check SSH connections
sudo netstat -tlnp | grep :22
```

---

## 📊 Backup and Maintenance

### Database Backup
```bash
# Manual backup
sudo -u postgres pg_dump connectly_db > backup.sql

# Restore backup
sudo -u postgres psql connectly_db < backup.sql

# Automated backup (already configured)
/home/django/backup.sh
```

### File Backup
```bash
# Project backup
tar -czf project_backup.tar.gz /home/django/connectly_project

# Restore project
tar -xzf project_backup.tar.gz -C /home/django/
```

### System Updates
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements_production.txt
```

---

## 🚨 Emergency Procedures

### Service Recovery
```bash
# If Django service fails
sudo systemctl restart connectly
sudo journalctl -u connectly -n 50

# If Nginx fails
sudo nginx -t
sudo systemctl restart nginx

# If database fails
sudo systemctl restart postgresql
sudo -u postgres psql -c "SELECT version();"
```

### Rollback Deployment
```bash
# Stop services
sudo systemctl stop connectly nginx

# Restore from backup
cd /home/django
tar -xzf project_backup.tar.gz

# Restart services
sudo systemctl start connectly nginx
```

### Complete Reset
```bash
# Stop all services
sudo systemctl stop connectly nginx postgresql

# Remove project
sudo rm -rf /home/django/connectly_project

# Re-run deployment script
./deploy_production.sh
```

---

## 📞 Support Commands

### Health Check
```bash
# Check all services
sudo systemctl status connectly nginx postgresql

# Check ports
sudo netstat -tlnp | grep -E ':(22|80|443|8000|5432)'

# Check disk space
df -h /home /var/log

# Check memory
free -h
```

### Performance Check
```bash
# Load average
uptime

# Process count
ps aux | wc -l

# Network connections
ss -tuln

# Disk I/O
iotop
```

---

## 🎯 Quick Deployment Commands

### One-Line Deployment
```bash
# Complete deployment (run as django user)
curl -sSL https://raw.githubusercontent.com/YOUR_USER/connectly_project/main/deploy_production.sh | bash
```

### Quick Service Restart
```bash
# Restart all services
sudo systemctl restart connectly nginx postgresql

# Check all services
sudo systemctl is-active connectly nginx postgresql
```

### Quick Log Check
```bash
# Check all logs at once
echo "=== Django Logs ===" && sudo tail -n 10 /var/log/django/connectly.log && echo "=== Nginx Error Logs ===" && sudo tail -n 10 /var/log/nginx/error.log && echo "=== System Logs ===" && sudo journalctl -u connectly -n 10
```

---

## 📚 File Locations

### Important Directories
- **Project**: `/home/django/connectly_project/`
- **Virtual Environment**: `/home/django/connectly_project/venv/`
- **Static Files**: `/home/django/connectly_project/staticfiles/`
- **Media Files**: `/home/django/connectly_project/media/`
- **Logs**: `/var/log/django/`, `/var/log/nginx/`
- **Backups**: `/home/django/backups/`

### Configuration Files
- **Django Settings**: `connectly_project/settings_production.py`
- **Gunicorn Config**: `gunicorn.conf.py`
- **Systemd Service**: `/etc/systemd/system/connectly.service`
- **Nginx Site**: `/etc/nginx/sites-available/connectly`
- **Environment**: `.env`

---

**🚀 Happy Deploying!**

*This quick reference covers the most essential commands and procedures for managing your Contabo VPS10 deployment.*
