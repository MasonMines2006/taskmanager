# Django Request-Response Flow

Understanding how Django processes a web request.

## 🔄 The Complete Flow

```
1. User visits URL
        ↓
2. urls.py matches URL pattern
        ↓
3. Calls the corresponding View
        ↓
4. View queries the Model (if needed)
        ↓
5. Model talks to Database via ORM
        ↓
6. View processes data
        ↓
7. View renders Template with data
        ↓
8. HTML returned to user's browser
```

## 📊 Detailed Example

Let's trace a request to view all tasks:

### Step 1: User Request
```
User types: http://127.0.0.1:8000/tasks/
```

### Step 2: URLs (taskmanager/urls.py)
```python
from django.urls import path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', views.task_list),  # ← Matches this pattern
]
```
**What happens:** Django finds the pattern and calls `views.task_list`

### Step 3: View (tasks/views.py)
```python
from django.shortcuts import render
from .models import Task

def task_list(request):
    # Query the model
    tasks = Task.objects.all()
    
    # Pass data to template
    context = {'tasks': tasks}
    
    # Render template with data
    return render(request, 'tasks/task_list.html', context)
```
**What happens:** View gets all tasks from database and prepares them for display

### Step 4: Model Query (tasks/models.py)
```python
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
```
**What happens:** ORM converts `Task.objects.all()` to SQL:
```sql
SELECT * FROM tasks_task;
```

### Step 5: Template (tasks/templates/tasks/task_list.html)
```html
<h1>My Tasks</h1>
<ul>
{% for task in tasks %}
    <li>
        {{ task.title }}
        {% if task.completed %}✓{% endif %}
    </li>
{% endfor %}
</ul>
```
**What happens:** Django template engine replaces `{{ task.title }}` with actual data

### Step 6: Response
```html
<h1>My Tasks</h1>
<ul>
    <li>Learn Django ✓</li>
    <li>Build a project</li>
    <li>Deploy to production</li>
</ul>
```
**What happens:** Browser receives and displays HTML

---

## 🏗️ MVT Architecture

Django uses **MVT** (Model-View-Template):

```
┌─────────────────────────────────────────────────┐
│                    BROWSER                       │
│              (User Interface)                    │
└──────────────────┬──────────────────────────────┘
                   │ HTTP Request
                   ↓
┌─────────────────────────────────────────────────┐
│                  urls.py                         │
│            (URL Router/Dispatcher)               │
└──────────────────┬──────────────────────────────┘
                   │ Calls View
                   ↓
┌─────────────────────────────────────────────────┐
│               VIEW (views.py)                    │
│         ┌─────────────────────────┐             │
│         │  Business Logic Layer   │             │
│         │  - Process request      │             │
│         │  - Query models         │             │
│         │  - Prepare data         │             │
│         └───────┬─────────┬───────┘             │
│                 │         │                      │
│       Queries   │         │   Renders            │
│                 ↓         ↓                      │
│    ┌─────────────┐   ┌──────────────┐          │
│    │   MODEL     │   │   TEMPLATE   │          │
│    │ (models.py) │   │  (.html)     │          │
│    └──────┬──────┘   └──────────────┘          │
│           │                                      │
└───────────┼──────────────────────────────────────┘
            │ ORM
            ↓
┌─────────────────────────────────────────────────┐
│              DATABASE (SQLite)                   │
│         (Data Persistence Layer)                 │
└─────────────────────────────────────────────────┘
```

### Comparison with MVC
| Django (MVT) | Traditional MVC | Purpose |
|--------------|-----------------|---------|
| Model | Model | Database layer |
| View | Controller | Business logic |
| Template | View | Presentation |

**Note:** Django calls it "View" but it acts like a Controller!

---

## 🎯 Key Components Explained

### 1. URLs (The Router)
**File:** `urls.py`

**Purpose:** Maps URLs to views

```python
urlpatterns = [
    path('', views.home),                    # /
    path('tasks/', views.task_list),         # /tasks/
    path('tasks/<int:pk>/', views.task_detail),  # /tasks/1/
    path('tasks/create/', views.task_create),    # /tasks/create/
]
```

**URL patterns can capture parameters:**
```python
path('tasks/<int:pk>/', views.task_detail)
# /tasks/5/ → calls task_detail(request, pk=5)
```

### 2. Views (The Controller)
**File:** `views.py`

**Purpose:** Handle requests, process data, return responses

```python
from django.shortcuts import render, redirect
from .models import Task

# Function-based view
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

# View that handles POST (form submission)
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        Task.objects.create(user=request.user, title=title)
        return redirect('task_list')
    return render(request, 'tasks/task_form.html')
```

**Views can:**
- Query the database (via Models)
- Process forms
- Handle authentication
- Return HTML (via Templates)
- Return JSON (for APIs)
- Redirect to other pages

### 3. Models (The Data Layer)
**File:** `models.py`

**Purpose:** Define data structure and database operations

```python
class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    
    def mark_complete(self):
        """Custom method"""
        self.completed = True
        self.save()
```

**Models provide:**
- Database schema definition
- ORM query interface
- Data validation
- Business logic methods

### 4. Templates (The Presentation Layer)
**File:** `templates/tasks/task_list.html`

**Purpose:** Generate HTML with dynamic data

```html
{% extends 'base.html' %}

{% block content %}
<h1>Tasks for {{ request.user.username }}</h1>

{% for task in tasks %}
    <div class="task {% if task.completed %}completed{% endif %}">
        <h3>{{ task.title }}</h3>
        <p>Created: {{ task.created_at|date:"M d, Y" }}</p>
    </div>
{% empty %}
    <p>No tasks yet!</p>
{% endfor %}
{% endblock %}
```

**Template features:**
- Variables: `{{ variable }}`
- Tags: `{% for %}`, `{% if %}`, etc.
- Filters: `{{ value|filter }}`
- Template inheritance: `{% extends %}`

---

## 🔁 Common Request Patterns

### Pattern 1: List View
```
User wants to see all tasks
    ↓
URL: /tasks/
    ↓
View: task_list(request)
    ↓
Model: Task.objects.filter(user=request.user)
    ↓
Template: task_list.html
    ↓
Display: List of tasks
```

### Pattern 2: Detail View
```
User wants to see one task
    ↓
URL: /tasks/5/
    ↓
View: task_detail(request, pk=5)
    ↓
Model: Task.objects.get(pk=5)
    ↓
Template: task_detail.html
    ↓
Display: Single task details
```

### Pattern 3: Create View (Form Submission)
```
User submits form to create task
    ↓
URL: /tasks/create/ (POST request)
    ↓
View: task_create(request)
    ↓
Process: request.POST.get('title')
    ↓
Model: Task.objects.create(...)
    ↓
Redirect: /tasks/ (back to list)
```

### Pattern 4: Update View
```
User edits a task
    ↓
URL: /tasks/5/edit/ (POST)
    ↓
View: task_update(request, pk=5)
    ↓
Model: Task.objects.get(pk=5)
        task.title = new_title
        task.save()
    ↓
Redirect: /tasks/5/ (to detail view)
```

### Pattern 5: Delete View
```
User deletes a task
    ↓
URL: /tasks/5/delete/ (POST)
    ↓
View: task_delete(request, pk=5)
    ↓
Model: Task.objects.get(pk=5).delete()
    ↓
Redirect: /tasks/ (back to list)
```

---

## 🔐 Request Object

Every view receives a `request` object with useful information:

```python
def my_view(request):
    # HTTP method
    request.method  # 'GET', 'POST', etc.
    
    # Current user
    request.user  # Current logged-in user
    request.user.is_authenticated  # True/False
    
    # GET parameters (?search=django)
    request.GET.get('search')
    
    # POST data (from forms)
    request.POST.get('title')
    
    # Session data
    request.session['cart'] = []
    
    # Uploaded files
    request.FILES.get('image')
    
    # Path info
    request.path  # '/tasks/5/'
    request.get_full_path()  # '/tasks/5/?page=2'
```

---

## 📤 Response Types

Views must return a response:

### 1. Render HTML
```python
from django.shortcuts import render
return render(request, 'template.html', context)
```

### 2. Redirect
```python
from django.shortcuts import redirect
return redirect('task_list')  # URL name
return redirect('/tasks/')     # URL path
```

### 3. JSON (for APIs)
```python
from django.http import JsonResponse
return JsonResponse({'status': 'success', 'task_id': 5})
```

### 4. Plain HTTP Response
```python
from django.http import HttpResponse
return HttpResponse("Hello, World!")
```

### 5. 404 Not Found
```python
from django.shortcuts import get_object_or_404
task = get_object_or_404(Task, pk=999)  # Raises 404 if not found
```

---

## 🎨 Putting It All Together

Here's a complete example of CRUD operations:

### urls.py
```python
from django.urls import path
from tasks import views

urlpatterns = [
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
]
```

### views.py
```python
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task

def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/list.html', {'tasks': tasks})

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/detail.html', {'task': task})

def task_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        Task.objects.create(user=request.user, title=title)
        return redirect('task_list')
    return render(request, 'tasks/form.html')

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.title = request.POST['title']
        task.completed = 'completed' in request.POST
        task.save()
        return redirect('task_detail', pk=pk)
    return render(request, 'tasks/form.html', {'task': task})

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/confirm_delete.html', {'task': task})
```

---

## 💡 Key Takeaways

1. **URLs route to Views** - `urls.py` is the entry point
2. **Views handle logic** - Process requests, query models
3. **Models manage data** - ORM abstracts database
4. **Templates display data** - HTML with Django template language
5. **Everything is connected** - Request flows through all layers

---

## 🎓 Next Steps

Now that you understand the flow:
1. Create your first view
2. Add URL routing
3. Build a template
4. Handle forms
5. Add user authentication

**Ready to build views? Let me know!** 🚀
