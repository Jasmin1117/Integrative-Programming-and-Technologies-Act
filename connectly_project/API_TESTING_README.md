# Connectly Project API Testing Guide

This guide provides comprehensive testing solutions for the Connectly Django project APIs using both Postman and automated Python testing.

## 📋 Table of Contents

1. [Postman Collection](#postman-collection)
2. [Automated Testing Script](#automated-testing-script)
3. [API Endpoints Overview](#api-endpoints-overview)
4. [Testing Workflow](#testing-workflow)
5. [Troubleshooting](#troubleshooting)

## 🔧 Postman Collection

### Import Instructions

1. **Download the Collection**: The `connectly_postman_collection.json` file contains all API endpoints organized by functionality.

2. **Import to Postman**:
   - Open Postman
   - Click "Import" button
   - Drag and drop the JSON file or click "Upload Files"
   - Select the `connectly_postman_collection.json` file

3. **Set Environment Variables**:
   - Create a new environment in Postman
   - Add the following variables:
     - `base_url`: `http://127.0.0.1:8000` (or your server URL)
     - `auth_token`: Leave empty (will be auto-populated)
     - `user_id`: Leave empty (will be auto-populated)
     - `post_id`: Leave empty (will be auto-populated)
     - `comment_id`: Leave empty (will be auto-populated)
     - `username`: `testuser` (or your test username)

### Collection Structure

The collection is organized into logical groups:

- **🔐 Authentication**: User registration, login, and token verification
- **👥 User Management**: CRUD operations on user accounts
- **📝 Posts**: Post creation, reading, updating, and deletion
- **💬 Comments**: Comment management on posts
- **❤️ Likes & Engagement**: Post likes and user interactions
- **📰 Newsfeed**: Different types of post feeds
- **🔧 Admin Operations**: Admin-specific endpoints with elevated privileges

### Testing Workflow in Postman

1. **Start with Authentication**:
   - Run "User Registration" to create a test account
   - Run "User Login" to get an authentication token
   - Run "Verify Authentication" to confirm token validity

2. **Test Core Functionality**:
   - Create a post using "Create Post"
   - Add comments using "Create Comment"
   - Test likes using "Like Post" and "Unlike Post"
   - Verify data retrieval with various GET endpoints

3. **Test Admin Operations** (if you have admin privileges):
   - Use admin endpoints to manage posts and comments
   - Test user management operations

## 🐍 Automated Testing Script

### Prerequisites

1. **Install Python Dependencies**:
   ```bash
   pip install -r test_requirements.txt
   ```

2. **Ensure Django Server is Running**:
   ```bash
   python manage.py runserver
   ```

### Running the Tests

1. **Basic Test Run**:
   ```bash
   python test_api_endpoints.py
   ```

2. **Custom Server URL**:
   ```bash
   python test_api_endpoints.py http://localhost:8000
   ```

3. **Test with Different Base URL**:
   ```bash
   python test_api_endpoints.py https://your-production-domain.com
   ```

### What the Script Tests

The automated testing script systematically tests:

- ✅ **Authentication Flow**: Registration → Login → Token Verification
- ✅ **User Management**: User CRUD operations
- ✅ **Post Operations**: Create, Read, Update, Delete posts
- ✅ **Comment System**: Add and retrieve comments
- ✅ **Like System**: Like/unlike posts and count likes
- ✅ **Newsfeed**: Various feed types
- ✅ **Admin Operations**: Elevated privilege operations
- ✅ **Data Cleanup**: Automatic cleanup of test data

### Test Output

The script provides:
- Real-time progress updates with emojis and status indicators
- Detailed success/failure information for each endpoint
- Response codes and content previews
- Comprehensive test summary with success rate
- JSON file with detailed test results (`api_test_results.json`)

## 🌐 API Endpoints Overview

### Base URL
```
http://127.0.0.1:8000
```

### Authentication Endpoints
- `POST /posts/users/` - User registration
- `POST /posts/login/` - User login
- `GET /posts/protected/` - Verify authentication

### User Management
- `GET /posts/users/` - List all users
- `GET /accounts/api/users/{id}/` - Get user by ID
- `PUT /accounts/api/users/{id}/update/` - Update user
- `POST /accounts/api/users/{id}/deactivate/` - Deactivate user
- `POST /accounts/api/users/{id}/activate/` - Activate user
- `DELETE /accounts/api/users/{id}/delete/` - Delete user

### Post Management
- `POST /posts/posts/create/` - Create post
- `GET /posts/posts/` - Get all posts
- `GET /posts/posts/{id}/` - Get post by ID
- `GET /posts/posts/my-posts/` - Get user's posts
- `PUT /posts/posts/edit/{id}/` - Edit post
- `DELETE /posts/posts/delete/{id}/` - Delete post
- `GET /posts/posts/public/` - Get public posts
- `GET /posts/posts/private/` - Get private posts

### Comment Management
- `GET /posts/posts/{id}/comments/` - Get post comments
- `POST /posts/posts/{id}/comments/create/` - Create comment
- `DELETE /posts/posts/{post_id}/comments/{comment_id}/delete/` - Delete comment

### Like System
- `POST /posts/posts/{id}/like/` - Like post
- `POST /posts/posts/{id}/unlike/` - Unlike post
- `GET /posts/posts/{id}/countlikes/` - Count post likes
- `GET /posts/posts/{id}/likedby/` - Get users who liked post

### Newsfeed
- `GET /posts/posts/feed/` - Main newsfeed
- `GET /posts/posts/feed/latest/` - Latest posts
- `GET /posts/posts/feed/public/` - Public posts feed

### Admin Operations
- `GET /posts/api/posts/{id}/` - Admin get post
- `PUT /posts/api/posts/{id}/update/` - Admin update post
- `DELETE /posts/api/posts/{id}/delete/` - Admin delete post
- `GET /posts/api/comments/{id}/` - Admin get comment
- `PUT /posts/api/comments/{id}/update/` - Admin update comment
- `DELETE /posts/api/comments/{id}/delete/` - Admin delete comment

## 🔄 Testing Workflow

### 1. Initial Setup
```bash
# Start Django server
python manage.py runserver

# In another terminal, run tests
python test_api_endpoints.py
```

### 2. Postman Testing
1. Import the collection
2. Set environment variables
3. Run authentication tests first
4. Test core functionality
5. Verify admin operations (if applicable)

### 3. Automated Testing
1. Run the complete test suite
2. Review test results
3. Check generated `api_test_results.json`
4. Address any failed tests

## 🚨 Troubleshooting

### Common Issues

1. **Server Not Running**:
   ```
   ❌ Server is not running at http://127.0.0.1:8000
   ```
   **Solution**: Start Django server with `python manage.py runserver`

2. **Authentication Failures**:
   - Check if user registration endpoint is working
   - Verify login credentials
   - Ensure token is being stored correctly

3. **Permission Denied**:
   - Some endpoints require admin privileges
   - Check user role and permissions
   - Verify authentication token is valid

4. **CSRF Token Issues**:
   - Django REST Framework handles CSRF automatically
   - Ensure proper Content-Type headers
   - Check if CSRF middleware is configured correctly

### Debug Mode

Enable Django debug mode for detailed error messages:
```python
# settings.py
DEBUG = True
```

### Logging

Check Django logs for detailed error information:
```bash
python manage.py runserver --verbosity 2
```

## 📊 Test Results

After running tests, you'll get:

1. **Console Output**: Real-time test progress and results
2. **JSON Report**: Detailed test results in `api_test_results.json`
3. **Summary**: Overall success rate and failed test details

### Sample Test Result
```json
{
  "endpoint": "/posts/users/",
  "method": "POST",
  "success": true,
  "response_code": 201,
  "details": "Response: {\"message\": \"User created successfully.\", \"user\": {...}}",
  "timestamp": "2024-01-15 14:30:25"
}
```

## 🔗 Additional Resources

- **Django REST Framework Documentation**: https://www.django-rest-framework.org/
- **Postman Learning Center**: https://learning.postman.com/
- **HTTP Status Codes**: https://httpstatuses.com/

## 📝 Notes

- The testing script automatically cleans up test data
- All tests use unique identifiers to avoid conflicts
- Admin operations require appropriate user privileges
- The collection includes pre-request and test scripts for automation
- Environment variables are automatically managed during testing

---

**Happy Testing! 🚀**

For issues or questions, check the Django server logs and ensure all dependencies are properly installed.
