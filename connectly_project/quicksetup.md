# Quick Setup - Run Locally

## Prerequisites
- Python 3.8+
- Git

## Quick Start

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd connectly_project
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 6. Start Development Server
```bash
# Option 1: Using Django directly
python manage.py runserver

# Option 2: Using Honcho (recommended)
honcho start
```

### 7. Access Application
- **Main Site**: http://127.0.0.1:8000/
- **Admin Dashboard**: http://127.0.0.1:8000/accounts/admin-dashboard/
- **Django Admin**: http://127.0.0.1:8000/admin/

## Login Credentials
Use the superuser credentials you created in step 5.

## Stop Server
Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting
- **Port already in use**: Kill existing process or use different port: `python manage.py runserver 8001`
- **Database errors**: Delete `db.sqlite3` and run `python manage.py migrate` again
- **Import errors**: Ensure virtual environment is activated and dependencies are installed
