# Task Manager - Django Learning Project

A simple task management application built to learn Django fundamentals.

## 🎯 What This Project Covers

- ✅ Django project and app structure
- ✅ Models and the Django ORM
- ✅ Database migrations
- ✅ Django admin interface
- ✅ User authentication (built-in)
- ✅ ForeignKey relationships

## 🚀 Quick Start

### Access the Admin Panel
1. Make sure the server is running: `python manage.py runserver`
2. Visit: http://127.0.0.1:8000/admin
3. Login:
   - **Username:** `admin`
   - **Password:** `admin123`
4. Click **Tasks** to manage your tasks!

### Use the Django Shell
```bash
python manage.py shell
```

Try creating tasks programmatically:
```python
from tasks.models import Task
from django.contrib.auth.models import User

user = User.objects.get(username='admin')
Task.objects.create(user=user, title="My first task!")
```

## 📁 Project Structure

```
taskmanager/
├── manage.py                  # Command-line utility
├── db.sqlite3                 # Database file (created after migrations)
├── taskmanager/               # Project configuration
│   ├── settings.py            # All settings
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI config
└── tasks/                     # Tasks app
    ├── models.py              # Task model
    ├── admin.py               # Admin configuration
    ├── views.py               # View functions (empty for now)
    └── migrations/            # Database migrations
```

## 📚 Learning Resources

- **LEARNING_GUIDE.md** - Detailed explanation of every step
- **ORM_CHEATSHEET.md** - Django ORM reference and examples

## 🔑 Important Commands

```bash
# Start the development server
python manage.py runserver

# Create migration files (after model changes)
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Open Django shell
python manage.py shell

# Create admin user
python manage.py createsuperuser
```

## 🎓 What You Learned

### 1. Django Project Structure
- Projects contain multiple apps
- Apps are self-contained modules
- Register apps in `INSTALLED_APPS`

### 2. Models (ORM)
```python
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
```
- Models define database structure
- Django handles SQL for you
- Relationships via ForeignKey

### 3. Migrations
- Track database changes over time
- `makemigrations` creates migration files
- `migrate` applies them to database

### 4. Django Admin
- Auto-generated admin interface
- Customize with `ModelAdmin` classes
- Great for internal tools

## 🚧 Next Steps

Want to continue learning? Here's what to add next:

### Phase 1: Basic Views
- Create a homepage that lists tasks
- Add URL routing
- Create HTML templates

### Phase 2: Forms
- Add task creation form
- Edit tasks from the web (not just admin)
- Delete tasks

### Phase 3: User Authentication
- Login/logout views
- User registration
- User-specific task views (can only see your tasks)

### Phase 4: Advanced Features
- Task priorities
- Due dates
- Categories/tags
- Search functionality
- Mark tasks complete from list view

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check if port 8000 is in use
lsof -i :8000

# Or run on different port
python manage.py runserver 8001
```

### Database issues?
```bash
# Delete database and start fresh
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Admin login not working?
```bash
# Reset admin password
python manage.py shell
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(username='admin')
>>> u.set_password('admin123')
>>> u.save()
>>> exit()
```

## 💡 Tips

1. **Read the Django docs** - They're excellent: https://docs.djangoproject.com/
2. **Use the shell** - Great for testing queries: `python manage.py shell`
3. **Check migrations** - Run `python manage.py showmigrations` to see status
4. **Debug with print()** - Add print statements in views.py
5. **Django Debug Toolbar** - Great tool for development (install separately)

## 📖 Recommended Reading Order

1. Read `LEARNING_GUIDE.md` - Understand what we built
2. Practice with `ORM_CHEATSHEET.md` - Try queries in the shell
3. Experiment in the admin panel - Create, edit, delete tasks
4. Modify the model - Add a new field (like priority or due_date)

## 🎯 Practice Challenges

1. **Add a "priority" field** to tasks (High, Medium, Low)
2. **Add a "due_date" field** using DateField
3. **Customize the admin** to show priority and due date
4. **Create 10 sample tasks** using the Django shell
5. **Query tasks** - Find all high-priority incomplete tasks

## 🤔 Questions?

If you're stuck, check:
1. Django documentation: https://docs.djangoproject.com/
2. Django Girls Tutorial: https://tutorial.djangogirls.org/
3. Django for Beginners: https://djangoforbeginners.com/

---

**Built with Django 6.0.5 | Python 3.14**

Ready to continue? Let's add views and templates next! 🚀
