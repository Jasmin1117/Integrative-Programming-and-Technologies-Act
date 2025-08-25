#!/bin/bash

# Connectly Django Project Deployment Script
# Run this script on your Contabo VPS10 server

set -e  # Exit on any error

echo "🚀 Starting Connectly Django Project Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y nginx postgresql postgresql-contrib
sudo apt install -y nodejs npm git
sudo apt install -y certbot python3-certbot-nginx
sudo apt install -y libpq-dev libjpeg-dev libpng-dev libfreetype6-dev
sudo apt install -y build-essential libssl-dev libffi-dev

# Create project directory
print_status "Setting up project directory..."
mkdir -p ~/connectly_project
cd ~/connectly_project

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install gunicorn psycopg2-binary

# Create logs directory
mkdir -p logs

# Create .env file template
print_status "Creating environment file template..."
cat > .env << 'EOF'
# Django Production Environment Variables
DEBUG=False
SECRET_KEY=your-super-secret-key-here-generate-a-new-one

# Database Configuration
DB_NAME=connectly_db
DB_USER=connectly_user
DB_PASSWORD=your_secure_database_password
DB_HOST=localhost
DB_PORT=5432

# Google OAuth (if using social login)
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret

# Allowed Hosts (comma-separated)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your_server_ip

# CSRF Trusted Origins (comma-separated, must include https://)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

print_warning "Please edit the .env file with your actual configuration values!"

# Create Gunicorn service file
print_status "Creating Gunicorn service file..."
sudo tee /etc/systemd/system/connectly.service > /dev/null << 'EOF'
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
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/connectly > /dev/null << 'EOF'
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/django/connectly_project;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /home/django/connectly_project;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/connectly_project/connectly.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable Nginx site
print_status "Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/connectly /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
print_status "Restarting Nginx..."
sudo systemctl restart nginx

# Enable Nginx and PostgreSQL
print_status "Enabling services..."
sudo systemctl enable nginx
sudo systemctl enable postgresql

# Create database and user
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql << 'EOF'
CREATE DATABASE connectly_db;
CREATE USER connectly_user WITH PASSWORD 'your_secure_database_password';
GRANT ALL PRIVILEGES ON DATABASE connectly_db TO connectly_user;
ALTER USER connectly_user CREATEDB;
\q
EOF

print_warning "Please change the database password in PostgreSQL!"

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R $USER:www-data ~/connectly_project
sudo chmod -R 755 ~/connectly_project

# Create firewall rules
print_status "Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

print_status "Deployment script completed!"
print_warning "Next steps:"
echo "1. Copy your Django project files to ~/connectly_project/"
echo "2. Edit the .env file with your actual configuration"
echo "3. Install your project dependencies: pip install -r requirements.txt"
echo "4. Run migrations: python manage.py migrate"
echo "5. Collect static files: python manage.py collectstatic --noinput"
echo "6. Start the Gunicorn service: sudo systemctl start connectly"
echo "7. Test your application at http://yourdomain.com"

print_status "For SSL certificate, run: sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
