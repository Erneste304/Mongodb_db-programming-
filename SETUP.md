# Petroleum Station Management System - Setup Guide

This guide provides step-by-step instructions for setting up and running the Petroleum Station Management System from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [MongoDB Atlas Setup](#mongodb-atlas-setup)
3. [Environment Configuration](#environment-configuration)
4. [Python Environment Setup](#python-environment-setup)
5. [Database Initialization](#database-initialization)
6. [Running the Backend](#running-the-backend)
7. [Running the Frontend](#running-the-frontend)
8. [First Login](#first-login)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- MongoDB Atlas account (free tier is sufficient)
- Git (optional, for version control)
- A modern web browser

## MongoDB Atlas Setup

### 1. Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" to create a free account
3. Complete the registration process

### 2. Create a Cluster

1. After logging in, click "Build a Database"
2. Choose "M0 Sandbox" (free tier)
3. Select a region closest to your location (e.g., "AWS (Africa) - Cape Town")
4. Name your cluster (e.g., "petroleum-station-db")
5. Click "Create"

### 3. Create Database User

1. Go to "Database Access" in the left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Enter a username and password (save these securely!)
5. Set "Database User Privileges" to "Read and write to any database"
6. Click "Add User"

### 4. Configure Network Access

1. Go to "Network Access" in the left sidebar
2. Click "Add IP Address"
3. Choose "Allow Access from Anywhere" (0.0.0.0/0) for development
4. Click "Confirm"

### 5. Get Connection String

1. Go to "Database" in the left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select "Python" and version "3.10 or later"
5. Copy the connection string

The connection string will look like:
```
mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
```

Replace `<username>` and `<password>` with your actual credentials.

## Environment Configuration

### 1. Navigate to Project Directory

```bash
cd /home/erneste/Documents/DB_Programming/petroleum_station
```

### 2. Create Environment File

```bash
cp .env.example .env
```

### 3. Edit .env File

Open `.env` in a text editor and update the following values:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.mongodb.net/petroleum_station?retryWrites=true&w=majority
DATABASE_NAME=petroleum_station

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration (optional, for background tasks)
REDIS_URL=redis://localhost:6379/0

# Application Settings
APP_NAME=Petroleum Station Management System
APP_VERSION=1.0.0
DEBUG=True

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Important:**
- Replace `your_username` and `your_password` with your MongoDB Atlas credentials
- Generate a strong random string for `SECRET_KEY` (you can use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- Keep your `.env` file secure and never commit it to version control

## Python Environment Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and related packages
- MongoDB drivers (motor, beanie, pymongo)
- Reflex (for frontend)
- Authentication libraries
- Other required dependencies

### 4. Verify Installation

```bash
python -c "import fastapi; import motor; import reflex; print('All packages installed successfully')"
```

## Database Initialization

### 1. Run Master Setup Script

The master setup script will:
- Create all required roles (superadmin, admin, accountant, etc.)
- Create all required permissions
- Create the initial superadmin user

```bash
python database/seeds/setup.py
```

### 2. Verify Setup

You should see output similar to:

```
============================================================
Petroleum Station Management System - Database Setup
============================================================

Step 1/2: Seeding roles...
Created role: superadmin
Created role: admin
...
✓ Roles seeded successfully

Step 2/2: Seeding permissions...
Created permission: users.create.user
Created permission: users.read.user
...
✓ Permissions seeded successfully

Step 3/3: Creating superadmin user...
Superadmin user created successfully!
Username: superadmin
Password: admin123
⚠️  IMPORTANT: Change the password after first login!

============================================================
✓ Database setup completed successfully!
============================================================
```

## Running the Backend

### 1. Start the FastAPI Server

```bash
uvicorn backend.main:app --reload --port 8000
```

You should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
Connected to MongoDB at mongodb+srv://...
Initialized Beanie ODM
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Verify Backend is Running

Open your browser and visit:
- http://localhost:8000 - API info
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- http://localhost:8000/health - Health check

### 3. Test Authentication

Using the Swagger UI at http://localhost:8000/docs:

1. Expand the `/auth/login` endpoint
2. Click "Try it out"
3. Enter:
   - username: `superadmin`
   - password: `admin123`
4. Click "Execute"
5. Copy the `access_token` from the response

## Running the Frontend

### 1. Initialize Reflex (First Time Only)

```bash
cd frontend
reflex init
```

Follow the prompts:
- App name: `petroleum_station`
- Initialize with template: `blank`

### 2. Run Reflex Development Server

```bash
reflex run
```

You should see:

```
Compiling your app...
Your app is running at: http://localhost:3000
```

### 3. Access the Application

Open your browser and visit: http://localhost:3000

## First Login

### 1. Login with Superadmin Credentials

- **Username:** `superadmin`
- **Password:** `admin123`

### 2. Change Password (Important!)

After first login, immediately change the superadmin password:

1. Go to user management
2. Find the superadmin user
3. Update the password to a strong, unique password

### 3. Create Additional Users

As superadmin, you can now:

1. Create admin users
2. Create accountant users
3. Create receptionist users
4. Create inventory manager users
5. Create staff users

Each user will have appropriate permissions based on their role.

## Troubleshooting

### MongoDB Connection Issues

**Problem:** "Connection refused" or "Authentication failed"

**Solution:**
- Verify your MongoDB Atlas credentials in `.env`
- Check that your IP is whitelisted in MongoDB Atlas Network Access
- Ensure your cluster is running (not paused)

### Python Import Errors

**Problem:** "Module not found" errors

**Solution:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version is 3.10 or higher

### Port Already in Use

**Problem:** "Port 8000 is already in use"

**Solution:**
- Kill the process using port 8000:
  ```bash
  # Linux/macOS
  lsof -ti:8000 | xargs kill -9
  
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```
- Or use a different port:
  ```bash
  uvicorn backend.main:app --reload --port 8001
  ```

### Reflex Not Starting

**Problem:** Reflex compilation errors

**Solution:**
- Ensure you're in the `frontend` directory
- Run `reflex init` again
- Check that all dependencies are installed

### Database Seed Issues

**Problem:** Seed script fails

**Solution:**
- Verify MongoDB connection string in `.env`
- Check that MongoDB Atlas cluster is running
- Run the setup script with verbose output if needed

## Development Tips

### Hot Reloading

- Backend: FastAPI auto-reloads on file changes when using `--reload`
- Frontend: Reflex auto-reloads on file changes during development

### API Testing

Use the Swagger UI at http://localhost:8000/docs to test all API endpoints interactively.

### Database Inspection

Use MongoDB Compass (GUI) or MongoDB Atlas web interface to inspect your database.

### Logs

- Backend logs appear in the terminal where uvicorn is running
- Frontend logs appear in the browser console (F12)

## Production Deployment

When deploying to production:

1. **Set DEBUG=False** in `.env`
2. **Use strong SECRET_KEY**
3. **Enable HTTPS** (use reverse proxy like Nginx)
4. **Configure proper CORS origins**
5. **Set up Redis** for background tasks
6. **Enable MongoDB Atlas backup**
7. **Monitor logs and errors**
8. **Set up regular database backups**
9. **Use environment-specific configuration**
10. **Implement rate limiting**

## Support

For issues or questions:
- Check the main README.md
- Review API documentation at http://localhost:8000/docs
- Check MongoDB Atlas status
- Verify all environment variables are set correctly

## Next Steps

After successful setup:

1. Change the superadmin password
2. Create admin users for daily operations
3. Create staff users with appropriate roles
4. Configure fuel prices in settings
5. Add fuel tanks to inventory
6. Set up initial fuel deliveries
7. Start processing transactions
8. Generate reports

## Security Checklist

- [ ] Changed default superadmin password
- [ ] Set strong SECRET_KEY
- [ ] Enabled HTTPS in production
- [ ] Configured proper CORS origins
- [ ] Enabled MongoDB Atlas authentication
- [ ] Set up database backups
- [ ] Implemented rate limiting
- [ ] Regularly update dependencies
- [ ] Monitor audit logs
- [ ] Review user permissions regularly

---

**System Version:** 1.0.0  
**Last Updated:** May 2026  
**Tech Stack:** FastAPI + MongoDB + Reflex
