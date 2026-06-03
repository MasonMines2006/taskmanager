# Django Task Manager - Learning Guide

## What We Built
A task management application where users can create, edit, and delete their own tasks through Django's admin interface.

---

## 📚 Complete Step-by-Step Explanation

### STEP 1: Installation & Project Setup

#### What happened:
```bash
pip install django
django-admin startproject taskmanager
```

#### What this means:
- **pip install django**: Installed Django framework (version 6.0.5)
- **django-admin startproject**: Created a new Django project

#### Project Structure Created:
```
taskmanager/
├── manage.py              ← Your command-line tool for this project
└── taskmanager/           ← Project configuration directory
    ├── settings.py        ← All project settings
    ├── urls.py            ← URL routing (which URLs go where)
    ├── wsgi.py/asgi.py    ← Server deployment files
    └── __init__.py        ← Makes this a Python package
```

**Key Learning:**
- `manage.py` is your friend - you'll use it for everything (run server, create database, etc.)
- The inner `taskmanager/` folder contains configuration
- Django projects are made up of multiple "apps"

---

### STEP 2: Creating the Tasks App

#### What happened:
```bash
python manage.py startapp tasks
```

#### What this means:
Django projects contain multiple **apps**. Each app handles a specific feature:
- A blog app
- A user authentication app
- A tasks app (what we created)

#### App Structure Created:
```
tasks/
├── models.py      ← Define database tables (our Task model)
├── views.py       ← Handle web requests and responses
├── admin.py       ← Register models for admin panel
├── apps.py        ← App configuration
├── tests.py       ← Write tests for your app
└── migrations/    ← Track database changes
```

**Key Learning:**
- Apps are reusable - you could copy this tasks app to another project
- Django follows MVT pattern: **Model-View-Template**

---

### STEP 3: Register the App

#### What happened:
We added `'tasks'` to `INSTALLED_APPS` in `settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',      # Built-in admin panel
    'django.contrib.auth',       # User authentication
    'django.contrib.contenttypes',
    'django.contrib.sessions',   # Session management
    'django.contrib.messages',   # Flash messages
    'django.contrib.staticfiles', # CSS/JS handling
    'tasks',                     # OUR APP!
]
```

**Key Learning:**
- Django won't recognize your app until you add it to `INSTALLED_APPS`
- Django comes with built-in apps (admin, auth, sessions, etc.)
- Each app in the list provides functionality to your project

---

### STEP 4: Create the Task Model (Django ORM)

#### What happened:
We created a `Task` class in `tasks/models.py`

```python
from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    # Relationship: Each task belongs to one user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    # Task data fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    
    # Auto-managed timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Newest first

    def __str__(self):
        return self.title
```

#### What each part means:

**1. `models.Model`**
- Your Task class inherits from Model
- This tells Django "this is a database table"

**2. Field Types:**
- `CharField`: Short text (like a title), needs max_length
- `TextField`: Long text (like a description), no length limit
- `BooleanField`: True/False checkbox
- `DateTimeField`: Date and time
- `ForeignKey`: Relationship to another model (User)

**3. ForeignKey Explained:**
```python
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
```
- Links each task to a User
- `on_delete=CASCADE`: If user is deleted, delete their tasks too
- `related_name='tasks'`: Lets you access user's tasks via `user.tasks.all()`

**4. Special Parameters:**
- `blank=True`: Field can be empty in forms
- `default=False`: Default value if none provided
- `auto_now_add=True`: Set once when created
- `auto_now=True`: Update every time you save

**5. Meta class:**
```python
class Meta:
    ordering = ['-created_at']  # Minus sign = descending order
```
Default sorting for queries (newest tasks first)

**6. `__str__` method:**
```python
def __str__(self):
    return self.title
```
How the object appears when printed (in admin, shell, etc.)

**Key Learning - The ORM (Object-Relational Mapping):**
- You write Python classes, Django creates database tables
- You never write SQL directly (Django does it for you)
- Each class = a table, each instance = a row

---

### STEP 5: Create and Apply Migrations

#### What happened:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### What this means:

**makemigrations:**
- Django looks at your models
- Creates a "migration file" (a recipe for database changes)
- File created: `tasks/migrations/0001_initial.py`

**migrate:**
- Reads all migration files
- Applies them to the database
- Creates actual tables in `db.sqlite3`

#### Behind the scenes:
Django converted your Python model into SQL:
```sql
CREATE TABLE tasks_task (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);
```

**Key Learning:**
- **Always run makemigrations after changing models**
- Migrations are version control for your database
- Django tracks which migrations have been applied

---

### STEP 6: Register Model in Admin Panel

#### What happened:
We configured `tasks/admin.py`

```python
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'completed', 'created_at')
    list_filter = ('completed', 'created_at', 'user')
    search_fields = ('title', 'description')
    list_editable = ('completed',)
```

#### What each part means:

**1. `@admin.register(Task)`**
- Decorator that registers the Task model with admin
- Makes Task appear in the admin panel

**2. `list_display`**
- Which columns to show in the admin list view
- Shows: title, user, completed status, and creation date

**3. `list_filter`**
- Adds filters in the sidebar
- Can filter by: completed, date, or user

**4. `search_fields`**
- Adds a search box
- Searches in title and description

**5. `list_editable`**
- Makes 'completed' checkbox editable directly in the list
- No need to open the task to mark it complete

**Key Learning:**
- Django admin is automatically generated from your models
- You can customize it extensively with ModelAdmin
- This is powerful for internal tools (staff can manage data without code)

---

### STEP 7: Create Superuser

#### What happened:
```bash
python manage.py createsuperuser
# Set password
```

#### What this means:
- Created an admin user account
- Username: `admin`
- Password: `admin123`

**Key Learning:**
- Superusers have full access to admin panel
- Django's auth system is built-in and robust
- In production, use strong passwords!

---

### STEP 8: Run the Server

#### What happened:
```bash
python manage.py runserver
```

#### What this means:
- Starts Django's development server
- Listens on http://127.0.0.1:8000/
- Auto-reloads when you change code

**Key Learning:**
- This is for development only (not production)
- Visit http://127.0.0.1:8000/admin to access admin panel
- Server runs until you press Ctrl+C

---

## 🎯 Core Django Concepts You Learned

### 1. **MVT Pattern** (Model-View-Template)
- **Model**: Data layer (tasks/models.py)
- **View**: Logic layer (tasks/views.py) - we'll add this next
- **Template**: Presentation layer (HTML files) - we'll add this next

### 2. **Django ORM**
- Write Python classes instead of SQL
- `models.ForeignKey` = relationships
- Automatic database table creation

### 3. **Migrations**
- Track database changes over time
- Version control for your schema
- Safe to apply in production

### 4. **Django Admin**
- Auto-generated admin interface
- Customizable with ModelAdmin classes
- Great for internal tools

### 5. **Django Apps**
- Projects contain multiple apps
- Apps are self-contained and reusable
- Register in INSTALLED_APPS

---

## 🚀 What You Can Do Right Now

### Access the Admin Panel:
1. Visit: http://127.0.0.1:8000/admin
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. Click "Tasks" to add/edit/delete tasks
4. Create some tasks and see them in the admin!

### Experiment with the ORM:
Open Django shell:
```bash
python manage.py shell
```

Try these commands:
```python
from tasks.models import Task
from django.contrib.auth.models import User

# Get admin user
user = User.objects.get(username='admin')

# Create a task
task = Task.objects.create(
    user=user,
    title="Learn Django ORM",
    description="Practice creating tasks with Python"
)

# Query all tasks
Task.objects.all()

# Filter tasks
Task.objects.filter(completed=False)

# Get user's tasks
user.tasks.all()

# Mark task complete
task.completed = True
task.save()
```

---

## 📖 Next Steps

### To continue learning, we can add:

1. **Custom Views** - Create web pages (not just admin)
2. **Templates** - HTML pages to display tasks
3. **Forms** - Let users add tasks from the website
4. **URLs** - Map URLs to views
5. **User Registration** - Let users sign up
6. **Authentication** - Login/logout views
7. **User-specific views** - Show only your tasks

### Django follows this flow:
```
URL → View → Model → Database
              ↓
         Template → HTML
```

---

## 🔑 Important Files Reference

| File | Purpose | You'll Edit Often? |
|------|---------|-------------------|
| `manage.py` | Command-line tool | ❌ Never touch |
| `settings.py` | Project configuration | ✅ Sometimes |
| `urls.py` | URL routing | ✅ Yes |
| `models.py` | Database tables | ✅ Yes |
| `views.py` | Request handlers | ✅ Yes |
| `admin.py` | Admin customization | ✅ Sometimes |
| `migrations/` | Database changes | ❌ Auto-generated |

---

## 🎓 Key Commands to Remember

```bash
# Create project
django-admin startproject projectname

# Create app
python manage.py startapp appname

# Make migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Open Python shell with Django loaded
python manage.py shell
```

---

## Questions to Test Your Understanding

1. What's the difference between a project and an app?
2. What does `on_delete=models.CASCADE` mean?
3. Why do we need to run both `makemigrations` AND `migrate`?
4. What does the `__str__` method do?
5. How would you add a new field "priority" to the Task model?

Try to answer these - they'll help solidify your learning!
