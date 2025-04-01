# Tailwind Setup Guide for Django Project

## Prerequisites
Ensure you have the following installed:
- Python (>= 3.x)
- Node.js (>= 16.x)
- npm (Node Package Manager)
- Virtual environment (recommended)

## 1. Clone the Project
If you haven't already, clone the project repository:
```bash
git clone https://github.com/Jasmin1117/Integrative-Programming-and-Technologies-Act
cd Integrative-Programming-and-Technologies-Act
```

## 2. Set Up Python Virtual Environment (Optional but Recommended)
```bash
python -m venv venv  # Create a virtual environment
source venv/bin/activate  # Activate (Mac/Linux)
venv\Scripts\activate  # Activate (Windows)
```

## 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 4. Install TailwindCSS in the Django Project
```bash
pip install django-tailwind
```

## 5. Install Node.js Dependencies for Tailwind
```bash
npm install
```
OR, if `package.json` is missing, run:
```bash
npm install tailwindcss postcss autoprefixer --save-dev
```

## 6. Initialize Tailwind
```bash
python manage.py tailwind install
```

## 7. Verify Tailwind Installation
Run the following command to start Tailwind:
```bash
python manage.py tailwind start
```
If Tailwind compiles successfully, the setup is complete.

## 8. Running the Project with Tailwind
To run both Django and Tailwind together, use:
```bash
honcho start
```

## 9. Common Issues & Fixes
- **If `tailwind` command is not found:**
  ```bash
  npm install --global tailwindcss
  ```
- **If `honcho` is not found:**
  ```bash
  pip install honcho
  ```

Your Django project should now be running with TailwindCSS successfully! 🎉

