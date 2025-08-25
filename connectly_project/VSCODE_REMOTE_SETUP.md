# 💻 VS Code Remote Development Setup Guide
## Connect to Your Contabo VPS10 Server for Seamless Development

This guide will walk you through setting up VS Code Remote Development to work directly on your deployed Django server.

---

## 📋 Prerequisites

- ✅ VS Code installed on your local machine
- ✅ Contabo VPS10 server deployed and running
- ✅ SSH access to your server
- ✅ SSH key pair configured

---

## 🔧 Step 1: Install VS Code Extensions

### Required Extensions
1. **Remote - SSH** - Core remote development functionality
2. **Python** - Python language support
3. **Django** - Django template support
4. **GitLens** - Enhanced Git functionality
5. **Thunder Client** - API testing (alternative to Postman)

### Installation Steps
1. Open VS Code
2. Press `Ctrl+Shift+X` (or `Cmd+Shift+X` on Mac)
3. Search for each extension and install them
4. Restart VS Code after installation

---

## 🔑 Step 2: Configure SSH Connection

### Local SSH Config Setup
**On your local machine, edit or create `~/.ssh/config`:**

**Windows (PowerShell as Administrator):**
```powershell
# Navigate to SSH config directory
cd $env:USERPROFILE\.ssh

# Create or edit config file
notepad config
```

**Linux/Mac:**
```bash
nano ~/.ssh/config
```

**Add your server configuration:**
```bash
Host contabo-vps10
    HostName YOUR_SERVER_IP
    User django
    Port 22
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ForwardAgent yes
    Compression yes
    TCPKeepAlive yes
```

**Replace `YOUR_SERVER_IP` with your actual server IP address.**

### Test SSH Connection
```bash
ssh contabo-vps10
```

You should connect successfully without password prompts.

---

## 🚀 Step 3: Connect to Remote Server

### Method 1: Command Palette
1. In VS Code, press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Remote-SSH: Connect to Host"
3. Select "contabo-vps10" from the list
4. Choose "Linux" when prompted for the platform
5. Wait for the connection to establish

### Method 2: Remote Explorer
1. Click the Remote Explorer icon in the left sidebar (or press `Ctrl+Shift+P` and search "Remote-SSH: Open SSH Configuration File")
2. Click the "+" button next to "SSH TARGETS"
3. Enter: `django@YOUR_SERVER_IP`
4. Select the SSH configuration file location
5. Click on your server to connect

### Method 3: Quick Connect
1. Press `Ctrl+Shift+P`
2. Type "Remote-SSH: Quick Open"
3. Enter: `django@YOUR_SERVER_IP`
4. Press Enter

---

## 📁 Step 4: Open Project Folder

### Navigate to Project Directory
1. Once connected, click "Open Folder" in the welcome screen
2. Navigate to `/home/django/connectly_project`
3. Click "OK" to open the project

### Alternative: Command Palette
1. Press `Ctrl+Shift+P`
2. Type "File: Open Folder"
3. Navigate to `/home/django/connectly_project`
4. Select the folder

---

## ⚙️ Step 5: Configure Python Environment

### Select Python Interpreter
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose the interpreter from your virtual environment: `/home/django/connectly_project/venv/bin/python`

### Install Python Extensions on Remote
VS Code will prompt you to install Python extensions on the remote server. Click "Install" when prompted.

---

## 🎯 Step 6: Configure Development Settings

### Create VS Code Workspace Settings
**Create `.vscode/settings.json` in your project root:**

```json
{
    "python.defaultInterpreterPath": "/home/django/connectly_project/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/node_modules": true,
        "**/.git": true
    },
    "python.envFile": "${workspaceFolder}/.env",
    "django.enabled": true,
    "django.trace": "verbose"
}
```

### Create VS Code Launch Configuration
**Create `.vscode/launch.json`:**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django: Run Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver", "0.0.0.0:8000"],
            "django": true,
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "DJANGO_SETTINGS_MODULE": "connectly_project.settings"
            }
        },
        {
            "name": "Django: Shell",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["shell"],
            "django": true,
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

---

## 🔧 Step 7: Development Workflow

### Running Django Commands
1. **Open Integrated Terminal**: `Ctrl+`` (backtick)
2. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```
3. **Run Django Commands**:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic
   ```

### Using VS Code Debugger
1. Set breakpoints in your Python code
2. Press `F5` or go to Run → Start Debugging
3. Select "Django: Run Server" configuration
4. Debug your application with full VS Code debugging features

### File Synchronization
- Files are automatically synchronized between your local VS Code and the remote server
- Changes are saved directly on the server
- No need to manually upload/download files

---

## 🚀 Step 8: Advanced Features

### Port Forwarding
**Forward local ports to remote server:**
1. Press `Ctrl+Shift+P`
2. Type "Remote-SSH: Forward Port"
3. Enter port number (e.g., 8000 for Django)
4. Access your app at `localhost:8000`

### Remote Terminal
- Use the integrated terminal for server commands
- Multiple terminal sessions
- Full access to server environment

### Git Integration
- Commit and push directly from VS Code
- View Git history and blame
- Branch management
- Pull requests (with GitHub extension)

### Extensions on Remote
Install these extensions on the remote server for enhanced development:

**Essential Extensions:**
- **Python** - Python language support
- **Django** - Django template support
- **GitLens** - Enhanced Git functionality
- **Thunder Client** - API testing
- **Auto Rename Tag** - HTML/XML tag renaming
- **Bracket Pair Colorizer** - Bracket matching
- **Path Intellisense** - File path autocomplete

**Installation:**
1. Go to Extensions (Ctrl+Shift+X)
2. Search for the extension
3. Click "Install on SSH: contabo-vps10"

---

## 🔒 Step 9: Security Best Practices

### SSH Key Security
- Use strong SSH keys (4096-bit RSA or Ed25519)
- Protect your private key with a passphrase
- Regularly rotate SSH keys
- Use different keys for different servers

### Server Access Control
- Limit SSH access to specific IP addresses
- Use fail2ban for brute force protection
- Monitor SSH access logs
- Regular security updates

### Development Security
- Never commit sensitive information (API keys, passwords)
- Use environment variables for configuration
- Regular dependency updates
- Code security scanning

---

## 🐛 Step 10: Troubleshooting

### Common Issues and Solutions

#### Connection Refused
```bash
# Check if SSH service is running
sudo systemctl status sshd

# Check firewall settings
sudo ufw status

# Verify SSH port
sudo netstat -tlnp | grep :22
```

#### Permission Denied
```bash
# Check file permissions
ls -la /home/django/connectly_project

# Fix permissions if needed
sudo chown -R django:django /home/django/connectly_project
```

#### Python Interpreter Not Found
```bash
# Check virtual environment
ls -la /home/django/connectly_project/venv/bin/

# Recreate virtual environment if needed
cd /home/django/connectly_project
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Extension Installation Issues
1. Check internet connectivity on server
2. Verify VS Code has necessary permissions
3. Try installing extensions manually
4. Check VS Code logs for errors

### Performance Optimization

#### Large Projects
- Use `.gitignore` to exclude unnecessary files
- Configure file watching exclusions
- Use workspace-specific settings

#### Network Issues
- Use SSH compression
- Optimize SSH connection settings
- Consider using SSH multiplexing

---

## 📚 Step 11: Useful Commands and Shortcuts

### VS Code Shortcuts
- `Ctrl+Shift+P` - Command Palette
- `Ctrl+Shift+E` - Explorer
- `Ctrl+Shift+X` - Extensions
- `Ctrl+`` - Integrated Terminal
- `F5` - Start Debugging
- `Ctrl+Shift+D` - Debug Panel

### Django Commands
```bash
# Development server
python manage.py runserver 0.0.0.0:8000

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Static files
python manage.py collectstatic

# Shell
python manage.py shell

# Tests
python manage.py test
```

### Server Commands
```bash
# Service management
sudo systemctl status connectly
sudo systemctl restart connectly
sudo systemctl restart nginx

# Log viewing
sudo journalctl -u connectly -f
sudo tail -f /var/log/nginx/error.log

# Process monitoring
htop
ps aux | grep gunicorn
```

---

## 🎉 Step 12: Development Workflow

### Daily Development Routine
1. **Connect to remote server** via VS Code
2. **Open project folder** `/home/django/connectly_project`
3. **Activate virtual environment** in terminal
4. **Make code changes** with full VS Code features
5. **Test changes** using integrated terminal or debugger
6. **Commit and push** using Git integration
7. **Deploy changes** using deployment script

### Code Quality Tools
- **Black** - Code formatting
- **Pylint** - Code linting
- **isort** - Import sorting
- **Pre-commit hooks** - Automated checks

### Testing and Debugging
- **Unit tests** - Run with `python manage.py test`
- **Debugging** - Use VS Code debugger
- **API testing** - Use Thunder Client
- **Performance monitoring** - Server monitoring tools

---

## 🔄 Step 13: Continuous Integration

### Automated Deployment
1. **Push to Git** from VS Code
2. **Trigger deployment** on server
3. **Run tests** automatically
4. **Deploy to production**

### Monitoring and Logs
- **Application logs** - `/var/log/django/connectly.log`
- **Nginx logs** - `/var/log/nginx/`
- **System logs** - `journalctl`
- **Performance metrics** - `htop`, `iotop`

---

## 📖 Additional Resources

### VS Code Documentation
- [Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)
- [Python Development](https://code.visualstudio.com/docs/python/python-tutorial)
- [Django Extension](https://marketplace.visualstudio.com/items?itemName=batisteo.vscode-django)

### Django Documentation
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/api-stability/)

### Server Management
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/)

---

## 🎯 Next Steps

1. **Set up automated testing** with pytest
2. **Configure CI/CD pipeline** with GitHub Actions
3. **Set up monitoring** with Prometheus/Grafana
4. **Implement backup strategies** for database and files
5. **Set up staging environment** for testing
6. **Configure logging aggregation** with ELK stack

---

**Happy Remote Development! 🚀**

*Your Django project is now accessible through VS Code with full development capabilities, directly on your production server.*
