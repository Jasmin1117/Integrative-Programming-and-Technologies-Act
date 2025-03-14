# API Test Cases Enhancing Functionality – User Features & Integrations

## Overview
This document contains test cases for verifying the functionality of the Connectly API.

---

# Test Cases


## 1. User Registration

### Test Case ID: TC-USER-REGISTER-001
**Feature:** User Registration (Regular User)

**Description:** Verify a user can register as a regular user.

**Preconditions:**
  - API endpoint `/users/` is available.
    
**Test Steps:**
  1. In Postman, create a POST request to `https://127.0.0.1:8000/posts/users/`.
  2. In the "Body" tab, select "raw" and "JSON".
  3. Enter a JSON payload containing a valid username, password, email, and role.
  4. Send the request.
  5. Check the "Status" code and response body.
  6. Verify the user is created in the database with `is_staff = False` and `role = "user"`.
     
**Expected Result:**
  - Status: 201 (Created).
  - Response JSON confirms successful user creation.
  - User exists in the database with correct attributes.

**Actual Result:**  

<img src="https://github.com/user-attachments/assets/47bece56-b4aa-45a8-b1f1-d040ba08698b" width="500">

**Database Update:**  

<img src="https://github.com/user-attachments/assets/a5123692-d4dd-4edf-9bed-2b9389b96347" width="1000">

User successfully created with the role of 'User'

**Status**: Pass✅

### Test Case ID: TC-ADMIN-REGISTER-002
**Feature:** User Registration (Admin User)

**Description:** Verify an admin user can be registered.

**Preconditions:**
  - API endpoint `/users/` is available.
    
**Test Steps:**
  1. In Postman, create a POST request to `http://127.0.0.1:8000/posts/users/`.
  2. In the "Body" tab, select "raw" and "JSON".
  3. Enter a JSON payload containing a valid admin username, password, email, and role.
  4. Send the request.
  5. Check the "Status" code and response body.
  6. Verify the user is created in the database with `is_staff = True` and `role = "admin"`.

**Expected Result:**
  - Status: 201 (Created).
  - Response JSON confirms successful user creation.
  - User exists in the database with correct attributes.
 
**Actual Result:**

<img src="https://github.com/user-attachments/assets/80e4c6f0-e4f2-4bb7-829c-af6f83f30177" width="500">

**Database Update:**

<img src="https://github.com/user-attachments/assets/e0cca5c5-bbe9-4e0e-9d2c-9ea31eee4632" width="1000">

User successfully created with the role of 'Admin'

**Status**: Pass✅

## 2. Post Management

### Test Case ID: TC-ADMIN-POST-DELETE-003
**Feature:** Admin Post Deletion

**Description:** Verify an admin can delete any post.

**Preconditions:**
  - Admin user is authenticated with a valid authorization token.
  - Post with ID 17 exists.
    
**Test Steps:**
  1. Create a DELETE request to `http://127.0.0.1:8000/posts/posts/17/`.
  2. Include a valid authentication token.
  3. Send the request.
  4. Check the "Status" code.
  5. Verify post 17 is deleted from the database.
     
**Expected Result:**
  - Status: 204 (No Content).
  - Post 17 deleted.

**Actual Result:**

Post created by user 'Roy":

<img src="https://github.com/user-attachments/assets/4ab7686f-336c-4268-85c3-a82d49926b47" width="500">


Deleted by admin 'Belle,' who was created earlier.:

<img src="https://github.com/user-attachments/assets/44e4803e-4782-498b-a58e-58f78594ab7c" width="500">


**Database Update:** 

No existing post found with Post ID 17:

<img src="https://github.com/user-attachments/assets/a7da737f-b788-439a-bedb-ec1e6a585133" width="700">


Admin successfully deleted a post from a regular user

**Status**: Pass✅



### Test Case ID: TC-USER-POST-DELETE-004
**Feature:** User Own Post Deletion

**Description:** Verify a user can delete their own post.

**Preconditions:**
  - User is authenticated with a valid authorization token.
  - Post 20 exists and is owned by the user.
    
**Test Steps:**
  1. Create a DELETE request to `http://127.0.0.1:8000/posts/posts/20/`.
  2. Include a valid authentication token.
  3. Send the request.
  4. Check the "Status" code.
  5. Verify post 20 is deleted.
     
**Expected Result:**
  - Status: 204 (No Content).
  - Post 20 deleted.

**Actual Result:**

Post created by user 'Roy":

<img src="https://github.com/user-attachments/assets/2f99764d-9a87-46bd-9410-aae9d399f79a" width="500">

User 'Roy' deleted his own post:

<img src="https://github.com/user-attachments/assets/32945b0c-cd1f-4e89-9027-f8bcdf2e918b" width="500">


**Database Update:**

No existing post found with Post ID 20:

<img src="https://github.com/user-attachments/assets/d3b2635d-f8ba-4138-9f0c-57fd8453c649" width="700">

User successfully deleted their own post

**Status**: Pass✅

### Test Case ID: TC-USER-POST-DELETE-005
**Feature:** User Unauthorized Post Deletion

**Description:** Verify a user cannot delete another user's post.

**Preconditions:**
  - User is authenticated with a valid authorization token.
  - Post 23 exists and is owned by another user.
    
**Test Steps:**
  1. Create a DELETE request to `http://127.0.0.1:8000/posts/posts/23/`.
  2. Include a valid authentication token.
  3. Send the request.
  4. Check the "Status" code.
  5. Verify post 23 still exists.

**Expected Result:**
  - Status: 403 (Forbidden).
  - Post 23 not deleted.

**Actual Result:**

Post created by user 'Roy":

<img src="https://github.com/user-attachments/assets/ba64589a-ddf3-402e-8687-b3f55394451b" width="500">

User 'Jakob' tried to delete a post belonging to user 'Roy'

<img src="https://github.com/user-attachments/assets/b2e46d51-419e-4749-b6f1-49a69fa2f844" width="500">

The user, Jakob, was successfully prevented from deleting another user's post

**Status**: Pass✅

### Test Case ID: TC-USER-POST-VISIBILITY-006  
**Feature:** Post Privacy (Public & Private)  

**Description:** Verify that a user can set a post as Public or Private and that private posts are only visible to the owner.  

**Preconditions:**  
  - User is authenticated with a valid authorization token.  
  - User has permission to create posts.  

**Test Steps:**  
  1. Create a POST request to `http://127.0.0.1:8000/posts/posts/`.  
  2. In the request body, include a `privacy` field with values `public` or `private`.  
  3. Send the request.  
  4. Retrieve the user’s feed (`GET /posts/feed/`).  
  5. Verify that:  
     - Public posts appear in all users’ feeds.  
     - Private posts are only visible to the post owner.  

**Expected Result:**  
  - Status: `201 Created`.  
  - Public posts are visible to all users.  
  - Private posts are visible only to the owner.  

**Actual Result:**  

Roy created a post with "private" visibility.

<img src="https://github.com/user-attachments/assets/6198b2d0-a34e-4544-ab4f-71a7660e628a" width="500">

A user's newsfeed does not show the private post created by Roy

<img src="https://github.com/user-attachments/assets/1ce39c69-ac97-48b4-9469-2a6236d06d22" width="500">

Roy's newsfeed shows his own private post.

<img src="https://github.com/user-attachments/assets/00752c84-c641-4ee1-9158-42ff27cb416e" width="500">


**Database Update:**  

<img src="https://github.com/user-attachments/assets/175ab0e3-99b8-4f57-921f-2e85f6a9bb14" width="500">

Private post successfully visible only to its author.

**Status**: Pass✅


## 3. Comment Management

### Test Case ID: TC-ADMIN-COMMENT-DELETE-007
**Feature:** Admin Comment Deletion

**Description:** Verify an admin can delete any comment.

**Preconditions:**
  - Admin user is authenticated with a valid authorization token.
  - Comment 20 exists in post 23
    
**Test Steps:**
  1. Create a DELETE request to `http://127.0.0.1:8000/posts/posts/23/comments/20/delete/`.
  2. Include a valid authentication token.
  3. Send the request.
  4. Check the "Status" code.
  5. Verify comment 20 is deleted.
     
**Expected Result:**
  - Status: 204 (No Content).
  - Comment 23 deleted.

**Actual Result:**

Comment created by user 'Jakob":

<img src="https://github.com/user-attachments/assets/f546a97c-83f4-432b-8966-899d79b58e73" width="500">

Comment deleted by admin 'Belle,':

<img src="https://github.com/user-attachments/assets/0515cdb9-455e-47d7-87fc-19e639df3c89" width="500">

**Database Update:**

<img src="https://github.com/user-attachments/assets/fce2c816-6c76-4f59-a172-fec26abe9de4" width="700">

Admin successfully deleted any comment from a regular user

**Status**: Pass✅


### Test Case ID: TC-USER-COMMENT-DELETE-008
**Feature:** User Own Comment Deletion

**Description:** Verify a user can delete their own comment.

**Preconditions:**
  - User is authenticated with a valid authorization token.
  - Comment 20 exists and is owned by the user.
    
**Test Steps:**
  1. Create a DELETE request to `http://127.0.0.1:8000/posts/posts/23/comments/22/delete/`.
  2. Include a valid authentication token.
  3. Send the request.
  4. Check the "Status" code.
  5. Verify comment 22 is deleted.
     
**Expected Result:**
  - Status: 204 (No Content).
  - Comment 22 deleted.

**Actual Result:**

Comment created by user 'Roy":

<img src="https://github.com/user-attachments/assets/177d9161-d473-4497-a0ae-708f478cd54e" width="500">

User 'Roy' deleted his own comment:

<img src="https://github.com/user-attachments/assets/97fb516b-a295-4ab1-aae1-cc90c981a22f" width="500">

**Database Update:**

<img src="https://github.com/user-attachments/assets/c2d19c28-d8d9-49d0-84f8-be2eb22639c7" width="700">

User successfully deleted their own comment

**Status**: Pass✅


### Test Case ID: TC-USER-COMMENT-DELETE-009
**Feature:** User Unauthorized Comment Deletion

**Description:** Verify a user cannot delete another user's comment.

**Preconditions:**
  - User is authenticated with a valid authorization token.
  - Comment 25 exists and is owned by another user.
    
**Test Steps:**
  1. Create a DELETE request to `http://127.0.0.1:8000/posts/posts/23/comments/25/delete/`.
  2. Include a valid authentication token.
  3. Send the request.
  4. Check the "Status" code.
  5. Verify comment 25 still exists.
     
**Expected Result:**
  - Status: 403 (Forbidden).
  - Comment 25 not deleted.

**Actual Result:**

Comment created by user 'Roy":

<img src="https://github.com/user-attachments/assets/3e71ff9f-f597-4613-8446-a46b50b9b423" width="500">

User 'Jakob' tried to delete a post belonging to user 'Roy'

<img src="https://github.com/user-attachments/assets/4a566c94-49d9-44de-8b83-f7f577d40a13" width="500">


The user, Jakob, was successfully prevented from deleting another user's comment

**Status**: Pass✅


---

## Notes
- Use Postman or cURL to execute the test cases.
- Any failed test case should be documented and reported for bug fixing.

---
