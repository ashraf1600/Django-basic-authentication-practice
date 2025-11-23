

 # Django Custom Authentication System

## Overview
This is a minimal task management system built with Django, featuring a custom user authentication system. This README explains how the authentication workflow operates and the responsibility of each component.

---

## 🏗️ Architecture Overview

```
User Request → URLs → Views → Forms → Models → Database
                ↓
            Templates (Response)
```

---

## 📁 Project Structure

```
taskmanager/
├── manage.py
├── taskmanager/
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py
└── accounts/
    ├── models.py            # User data structure
    ├── forms.py             # Form validation
    ├── views.py             # Business logic
    ├── urls.py              # App URL routing
    ├── admin.py             # Admin panel config
    └── templates/
        └── accounts/
            ├── base.html
            ├── signup.html
            ├── login.html
            └── dashboard.html
```

---

## 🔐 Authentication Workflow

### 1. **User Model (models.py)**

**Purpose:** Defines the structure of user data in the database.

```python
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
```

**How it works:**
- Extends Django's built-in `AbstractUser` class
- Inherits default fields: `username`, `password`, `email`, `first_name`, `last_name`, `is_staff`, etc.
- Allows adding custom fields like `bio`
- Each user is stored as a row in the database

**Responsibility:**
- Data structure definition
- Database table creation
- Data validation at model level

---

### 2. **Settings Configuration (settings.py)**

**Purpose:** Configure Django to use the custom user model.

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

**How it works:**
- Tells Django to use `CustomUser` instead of the default `User` model
- Must be set BEFORE the first migration
- All authentication references point to this model

**Important Settings:**
```python
LOGIN_URL = 'login'                    # Redirect here if not authenticated
LOGIN_REDIRECT_URL = 'dashboard'       # Redirect after successful login
LOGOUT_REDIRECT_URL = 'login'          # Redirect after logout
```

---

### 3. **Forms (forms.py)**

**Purpose:** Handle user input validation and data processing.

#### SignUp Form
```python
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
```

**How it works:**
- Extends `UserCreationForm` for built-in password validation
- Validates that `password1` and `password2` match
- Checks password strength (minimum 8 characters, not too common, etc.)
- Automatically hashes password before saving

#### Login Form
```python
class LoginForm(AuthenticationForm):
    # Custom styling and validation
```

**Responsibilities:**
- Client-side and server-side validation
- Data cleaning and sanitization
- Error message generation
- HTML form rendering

---

### 4. **Views (views.py)**

**Purpose:** Handle HTTP requests and responses, implement business logic.

#### Sign Up View

```python
def signup_view(request):
    if request.method == 'POST':           # Form submitted
        form = SignUpForm(request.POST)    # Create form with submitted data
        if form.is_valid():                # Validate data
            user = form.save()             # Save to database (password auto-hashed)
            login(request, user)           # Log user in immediately
            messages.success(request, 'Account created!')
            return redirect('dashboard')   # Redirect to dashboard
    else:                                  # GET request (initial page load)
        form = SignUpForm()                # Empty form
    return render(request, 'accounts/signup.html', {'form': form})
```

**Workflow:**
1. User fills out signup form
2. Browser sends POST request with form data
3. View receives data and creates `SignUpForm` instance
4. Form validates data (username unique, passwords match, etc.)
5. If valid, password is hashed using PBKDF2 algorithm
6. User object saved to database
7. `login()` function creates session
8. User redirected to dashboard

---

#### Login View

```python
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)  # Verify credentials
            if user is not None:
                login(request, user)      # Create session
                return redirect('dashboard')
```

**Workflow:**
1. User submits username and password
2. `authenticate()` function:
   - Queries database for username
   - Hashes submitted password
   - Compares hashed password with stored hash
   - Returns user object if match, None otherwise
3. `login()` function:
   - Creates session in database
   - Stores session ID in browser cookie
   - Associates session with user
4. User redirected to dashboard

**Key Functions:**
- `authenticate(username, password)`: Verifies credentials
- `login(request, user)`: Creates session
- Returns `None` if credentials invalid

---

#### Logout View

```python
@login_required
def logout_view(request):
    logout(request)                    # Destroy session
    messages.info(request, 'Logged out!')
    return redirect('login')
```

**Workflow:**
1. User clicks logout button
2. `logout()` function:
   - Deletes session from database
   - Clears session cookie from browser
3. User redirected to login page

**`@login_required` decorator:**
- Checks if user has valid session
- If not authenticated, redirects to `LOGIN_URL`
- If authenticated, allows access to view

---

#### Protected View (Dashboard)

```python
@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})
```

**How it works:**
- `@login_required` ensures only authenticated users access
- `request.user` contains current user's data
- If not logged in, automatic redirect to login page

---

### 5. **URL Routing (urls.py)**

**Purpose:** Map URLs to view functions.

```python
# accounts/urls.py
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]

# taskmanager/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
```

**How it works:**
- URL pattern matching
- Routes requests to appropriate view function
- Named URLs for easy reference in templates

**Example:**
- User visits `/accounts/signup/`
- Django matches pattern `accounts/` + `signup/`
- Calls `signup_view()` function

---

### 6. **Templates**

**Purpose:** Render HTML pages for user interface.

#### Template Inheritance
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Task Manager{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

<!-- signup.html -->
{% extends 'accounts/base.html' %}
{% block content %}
    <!-- Signup form here -->
{% endblock %}
```

**Key Template Tags:**
- `{% csrf_token %}`: CSRF protection token
- `{{ form.username }}`: Render form field
- `{% url 'login' %}`: Generate URL from name
- `{{ form.username.errors }}`: Display validation errors

---

## 🔒 Security Features

### 1. **Password Hashing**

**How it works:**
- Plain text passwords are NEVER stored
- Django uses PBKDF2 algorithm with SHA256 hash
- Each password has unique salt

**Example:**
```
Input: "mypassword123"
Stored: "pbkdf2_sha256$260000$xyz123$abc456def789..."
```

**Process:**
- 260,000 iterations of hashing
- Makes brute-force attacks extremely slow
- Even if database is compromised, passwords are safe

---

### 2. **CSRF Protection**

**What is CSRF?**
Cross-Site Request Forgery - malicious websites making requests on behalf of logged-in users.

**How Django prevents it:**
```html
<form method="post">
    {% csrf_token %}  <!-- Generates hidden token -->
    <!-- form fields -->
</form>
```

**Process:**
1. Server generates unique token per session
2. Token embedded in form as hidden field
3. On form submission, server validates token
4. Request rejected if token missing or invalid

---

### 3. **Session Management**

**How sessions work:**

1. **Login:**
   - Server creates session ID (e.g., `a1b2c3d4e5f6...`)
   - Stores session data in database
   - Sends session ID to browser as cookie

2. **Authenticated Requests:**
   - Browser sends session cookie with each request
   - Server looks up session in database
   - Retrieves associated user
   - Populates `request.user`

3. **Logout:**
   - Session deleted from database
   - Cookie cleared from browser

**Session Storage:**
```python
# Database session table
session_key: "a1b2c3d4e5f6..."
session_data: {"_auth_user_id": "123", ...}
expire_date: "2024-01-15 10:30:00"
```

---

## 🔄 Complete Authentication Flows

### Sign Up Flow
```
1. User → visits /accounts/signup/
2. Browser → GET request → signup_view()
3. View → renders signup.html with empty form
4. User → fills form → submits
5. Browser → POST request with data
6. signup_view() → receives data
7. SignUpForm → validates data
   - Username unique?
   - Email valid?
   - Passwords match?
   - Password strong enough?
8. If valid → user.save()
9. Password → hashed automatically
10. Database → stores user record
11. login() → creates session
12. Session ID → stored in cookie
13. Redirect → dashboard
```

### Login Flow
```
1. User → visits /accounts/login/
2. Browser → GET request → login_view()
3. View → renders login.html
4. User → enters credentials → submits
5. Browser → POST request
6. login_view() → receives data
7. authenticate() → queries database
   - Find user by username
   - Hash submitted password
   - Compare with stored hash
8. If match → return user object
9. login() → create session
10. Session → stored in database
11. Cookie → sent to browser
12. Redirect → dashboard
```

### Accessing Protected Page
```
1. User → visits /accounts/dashboard/
2. @login_required → checks session
3. If no session → redirect to login
4. If valid session:
   - Lookup user from session
   - Populate request.user
   - Render dashboard with user data
```

### Logout Flow
```
1. User → clicks logout
2. Browser → POST request → logout_view()
3. logout() → deletes session from database
4. Cookie → cleared from browser
5. Redirect → login page
```

---

## 📊 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **models.py** | - Define user data structure<br>- Database schema<br>- Field validation rules |
| **forms.py** | - Input validation<br>- Data cleaning<br>- Error messages<br>- Form rendering |
| **views.py** | - Request handling<br>- Business logic<br>- Authentication flow<br>- Response generation |
| **urls.py** | - URL routing<br>- Pattern matching<br>- View mapping |
| **templates/** | - HTML rendering<br>- User interface<br>- Display logic |
| **settings.py** | - Project configuration<br>- Security settings<br>- App registration |
| **admin.py** | - Admin interface<br>- Model registration<br>- Custom admin views |

---

## 🚀 Setup Instructions

### 1. Install Django
```bash
pip install django
```

### 2. Create Project
```bash
django-admin startproject taskmanager
cd taskmanager
python manage.py startapp accounts
```

### 3. Configure Settings
Add to `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'accounts',
]

AUTH_USER_MODEL = 'accounts.CustomUser'
```

### 4. Create Files
- Copy code from artifacts to respective files
- Create templates folder structure

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```

### 8. Access Application
- Signup: `http://127.0.0.1:8000/accounts/signup/`
- Login: `http://127.0.0.1:8000/accounts/login/`
- Dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
- Admin: `http://127.0.0.1:8000/admin/`

---

## 🔍 Key Django Functions

| Function | Purpose |
|----------|---------|
| `authenticate(username, password)` | Verify user credentials |
| `login(request, user)` | Create session for user |
| `logout(request)` | Destroy user session |
| `@login_required` | Decorator to protect views |
| `user.set_password(password)` | Hash and set password |
| `user.check_password(password)` | Verify password |

---

## 🛡️ Best Practices

1. **Always use `@login_required`** for protected views
2. **Never store plain text passwords**
3. **Always include `{% csrf_token %}`** in forms
4. **Use `redirect()`** after POST requests
5. **Validate user input** in forms and views
6. **Set strong `SECRET_KEY`** in production
7. **Use HTTPS** in production
8. **Enable session security** settings

---

## 📚 Next Steps

After understanding authentication, you can:
1. Add password reset functionality
2. Implement email verification
3. Add social authentication (Google, Facebook)
4. Create user profiles
5. Add two-factor authentication
6. Build the task management features

---

## 🐛 Common Issues

**Issue:** `AUTH_USER_MODEL` error
**Solution:** Set before first migration, or delete database and migrations

**Issue:** Template not found
**Solution:** Check `INSTALLED_APPS` and `APP_DIRS = True`

**Issue:** CSRF token missing
**Solution:** Add `{% csrf_token %}` in forms

**Issue:** Login not persisting
**Solution:** Check `django.contrib.sessions` in `INSTALLED_APPS`

---

This authentication system provides a solid foundation for building secure web applications with Django!


