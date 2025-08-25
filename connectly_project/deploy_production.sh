#!/bin/bash

# 🚀 Production Deployment Script for Connectly Django Project
# This script automates the deployment process on Contabo VPS10

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
PROJECT_NAME="connectly"
PROJECT_DIR="/home/django/connectly_project"
VENV_DIR="$PROJECT_DIR/venv"
DB_NAME="connectly_db"
DB_USER="connectly_user"
SERVICE_NAME="connectly"
NGINX_SITE="connectly"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as django user."
    fi
}

# Check if running as django user
check_user() {
    if [[ $(whoami) != "django" ]]; then
        error "This script must be run as django user"
    fi
}

# Update system packages
update_system() {
    log "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    log "System packages updated successfully"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Python and development tools
    sudo apt install -y python3 python3-pip python3-venv python3-dev
    
    # Web server and database
    sudo apt install -y nginx postgresql postgresql-contrib
    
    # Node.js for Tailwind CSS
    sudo apt install -y nodejs npm
    
    # Additional dependencies
    sudo apt install -y git curl wget unzip
    
    # SSL certificate tools
    sudo apt install -y certbot python3-certbot-nginx
    
    # System libraries for Python packages
    sudo apt install -y libpq-dev libjpeg-dev libpng-dev libfreetype6-dev
    sudo apt install -y build-essential libssl-dev libffi-dev
    
    log "System dependencies installed successfully"
}

# Setup PostgreSQL database
setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Start PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Check if database exists
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
        warning "Database $DB_NAME already exists"
    else
        # Create database and user
        sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$(openssl rand -base64 32)';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\q
EOF
        log "Database $DB_NAME created successfully"
    fi
}

# Setup Python virtual environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    cd $PROJECT_DIR
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv venv
        log "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install production requirements
    if [ -f "requirements_production.txt" ]; then
        pip install -r requirements_production.txt
        log "Production requirements installed"
    else
        pip install -r requirements.txt
        # Install additional production packages
        pip install gunicorn psycopg2-binary
        log "Requirements installed with production packages"
    fi
    
    log "Python environment setup completed"
}

# Configure Django settings
configure_django() {
    log "Configuring Django settings..."
    
    cd $PROJECT_DIR
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << EOF
DEBUG=False
SECRET_KEY=$(openssl rand -base64 50)
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://localhost
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
EOF
        log ".env file created with secure values"
    fi
    
    # Create production settings if it doesn't exist
    if [ ! -f "connectly_project/settings_production.py" ]; then
        warning "Production settings file not found. Please create it manually."
    fi
    
    log "Django configuration completed"
}

# Run Django migrations
run_migrations() {
    log "Running Django migrations..."
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # Run migrations
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then
        warning "No superuser found. Please create one manually:"
        warning "cd $PROJECT_DIR && source venv/bin/activate && python manage.py createsuperuser"
    fi
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    log "Django migrations completed"
}

# Configure Gunicorn
configure_gunicorn() {
    log "Configuring Gunicorn..."
    
    cd $PROJECT_DIR
    
    # Create Gunicorn configuration
    cat > gunicorn.conf.py << EOF
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
EOF
    
    log "Gunicorn configuration created"
}

# Configure systemd service
configure_systemd() {
    log "Configuring systemd service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Connectly Django Application
After=network.target postgresql.service

[Service]
User=django
Group=django
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py connectly_project.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    
    log "Systemd service configured"
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    # Create Nginx site configuration
    sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null << EOF
server {
    listen 80;
    server_name _;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;

    # SSL Configuration (will be updated by Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/\$server_name/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/\$server_name/privkey.pem;
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
        alias $PROJECT_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
EOF
    
    # Enable site and remove default
    sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    sudo nginx -t
    
    log "Nginx configuration completed"
}

# Setup logging
setup_logging() {
    log "Setting up logging..."
    
    # Create log directory
    sudo mkdir -p /var/log/django
    sudo chown django:django /var/log/django
    
    # Create log file
    sudo touch /var/log/django/connectly.log
    sudo chown django:django /var/log/django/connectly.log
    
    log "Logging setup completed"
}

# Setup backup script
setup_backup() {
    log "Setting up backup script..."
    
    cd /home/django
    
    # Create backup script
    cat > backup.sh << 'EOF'
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
EOF
    
    # Make executable
    chmod +x backup.sh
    
    # Add to crontab for daily backups at 2 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * /home/django/backup.sh") | crontab -
    
    log "Backup script setup completed"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start Django service
    sudo systemctl start $SERVICE_NAME
    sudo systemctl status $SERVICE_NAME --no-pager
    
    # Start Nginx
    sudo systemctl restart nginx
    sudo systemctl status nginx --no-pager
    
    log "Services started successfully"
}

# Security hardening
security_hardening() {
    log "Applying security hardening..."
    
    # Configure firewall
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    sudo ufw --force enable
    
    # Configure Fail2Ban
    sudo tee /etc/fail2ban/jail.local > /dev/null << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF
    
    sudo systemctl enable fail2ban
    sudo systemctl start fail2ban
    
    log "Security hardening completed"
}

# Final checks
final_checks() {
    log "Performing final checks..."
    
    # Check if services are running
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        log "✅ Django service is running"
    else
        error "❌ Django service is not running"
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        log "✅ Nginx is running"
    else
        error "❌ Nginx is not running"
    fi
    
    if sudo systemctl is-active --quiet postgresql; then
        log "✅ PostgreSQL is running"
    else
        error "❌ PostgreSQL is not running"
    fi
    
    # Check if application is accessible
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        log "✅ Django application is accessible on port 8000"
    else
        warning "⚠️  Django application is not accessible on port 8000"
    fi
    
    log "Final checks completed"
}

# Main deployment function
main() {
    log "🚀 Starting production deployment..."
    
    # Check prerequisites
    check_root
    check_user
    
    # Deployment steps
    update_system
    install_dependencies
    setup_database
    setup_python_env
    configure_django
    run_migrations
    configure_gunicorn
    configure_systemd
    configure_nginx
    setup_logging
    setup_backup
    security_hardening
    start_services
    final_checks
    
    log "🎉 Production deployment completed successfully!"
    log ""
    log "📋 Next steps:"
    log "1. Configure your domain DNS to point to this server"
    log "2. Obtain SSL certificate: sudo certbot --nginx -d yourdomain.com"
    log "3. Update .env file with your actual domain and OAuth credentials"
    log "4. Test your application at https://yourdomain.com"
    log ""
    log "🔧 Useful commands:"
    log "- Check service status: sudo systemctl status $SERVICE_NAME"
    log "- View logs: sudo journalctl -u $SERVICE_NAME -f"
    log "- Restart service: sudo systemctl restart $SERVICE_NAME"
    log "- Check Nginx: sudo nginx -t && sudo systemctl restart nginx"
    log ""
    log "📚 For VS Code remote development:"
    log "- Install Remote-SSH extension"
    log "- Connect to: django@$(hostname -I | awk '{print $1}')"
    log "- Open folder: $PROJECT_DIR"
}

# Run main function
main "$@"
