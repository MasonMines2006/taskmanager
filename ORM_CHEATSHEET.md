# Django ORM Cheatsheet - Task Manager

## What is the ORM?
**ORM = Object-Relational Mapping**
- You write Python code
- Django converts it to SQL
- You never write SQL directly!

---

## Common Operations

### CREATE - Adding Tasks

```python
from tasks.models import Task
from django.contrib.auth.models import User

# Get a user
user = User.objects.get(username='admin')

# Method 1: Create and save
task = Task(
    user=user,
    title="My First Task",
    description="Learning Django is fun!",
    completed=False
)
task.save()  # Saves to database

# Method 2: Create in one step
task = Task.objects.create(
    user=user,
    title="Another Task",
    description="This saves automatically"
)

# Method 3: Bulk create
Task.objects.bulk_create([
    Task(user=user, title="Task 1"),
    Task(user=user, title="Task 2"),
    Task(user=user, title="Task 3"),
])
```

**SQL equivalent:**
```sql
INSERT INTO tasks_task (user_id, title, description, completed, created_at, updated_at)
VALUES (1, 'My First Task', 'Learning Django is fun!', 0, NOW(), NOW());
```

---

### READ - Querying Tasks

```python
# Get ALL tasks
all_tasks = Task.objects.all()

# Get ONE task (raises error if not found or multiple found)
task = Task.objects.get(id=1)
task = Task.objects.get(title="My First Task")

# Filter tasks (returns QuerySet)
incomplete_tasks = Task.objects.filter(completed=False)
user_tasks = Task.objects.filter(user=user)
recent_tasks = Task.objects.filter(created_at__gte='2026-01-01')

# Exclude tasks
completed = Task.objects.exclude(completed=False)  # Only completed tasks

# Chain filters
my_incomplete = Task.objects.filter(user=user).filter(completed=False)
# Same as:
my_incomplete = Task.objects.filter(user=user, completed=False)

# Get first/last
first_task = Task.objects.first()
last_task = Task.objects.last()

# Check if exists
exists = Task.objects.filter(title="Learn Django").exists()

# Count
total_tasks = Task.objects.count()
incomplete_count = Task.objects.filter(completed=False).count()
```

**SQL equivalent:**
```sql
SELECT * FROM tasks_task;
SELECT * FROM tasks_task WHERE id = 1;
SELECT * FROM tasks_task WHERE completed = 0;
SELECT COUNT(*) FROM tasks_task;
```

---

### UPDATE - Modifying Tasks

```python
# Method 1: Get, modify, save
task = Task.objects.get(id=1)
task.completed = True
task.title = "Updated Title"
task.save()  # Saves changes

# Method 2: Update multiple at once
Task.objects.filter(completed=False).update(completed=True)

# Update specific task
Task.objects.filter(id=1).update(title="New Title")
```

**SQL equivalent:**
```sql
UPDATE tasks_task SET completed = 1 WHERE id = 1;
UPDATE tasks_task SET completed = 1 WHERE completed = 0;
```

---

### DELETE - Removing Tasks

```python
# Delete one task
task = Task.objects.get(id=1)
task.delete()

# Delete multiple
Task.objects.filter(completed=True).delete()

# Delete all (be careful!)
Task.objects.all().delete()
```

**SQL equivalent:**
```sql
DELETE FROM tasks_task WHERE id = 1;
DELETE FROM tasks_task WHERE completed = 1;
```

---

## Field Lookups (Filters)

### Exact Match
```python
Task.objects.filter(title="Learn Django")
Task.objects.filter(completed=True)
```

### Contains (case-sensitive)
```python
Task.objects.filter(title__contains="Django")
# Matches: "Learn Django", "Django is great"
```

### Case-insensitive contains
```python
Task.objects.filter(title__icontains="django")
# Matches: "Learn Django", "DJANGO", "django"
```

### Starts with / Ends with
```python
Task.objects.filter(title__startswith="Learn")
Task.objects.filter(title__endswith="Tutorial")
Task.objects.filter(title__istartswith="learn")  # Case-insensitive
```

### Greater than / Less than
```python
# Tasks created after a date
Task.objects.filter(created_at__gt='2026-05-01')  # Greater than
Task.objects.filter(created_at__gte='2026-05-01')  # Greater than or equal
Task.objects.filter(created_at__lt='2026-05-01')  # Less than
Task.objects.filter(created_at__lte='2026-05-01')  # Less than or equal
```

### In a list
```python
Task.objects.filter(id__in=[1, 2, 3, 4])
Task.objects.filter(title__in=["Task 1", "Task 2"])
```

### Range
```python
import datetime
start = datetime.date(2026, 5, 1)
end = datetime.date(2026, 5, 31)
Task.objects.filter(created_at__range=[start, end])
```

### Is null
```python
Task.objects.filter(description__isnull=True)  # No description
Task.objects.filter(description__isnull=False)  # Has description
```

---

## Relationships (ForeignKey)

Our Task model has: `user = models.ForeignKey(User, ...)`

### Access user from task
```python
task = Task.objects.get(id=1)
print(task.user.username)  # Access the related user
print(task.user.email)
```

### Access tasks from user (reverse relation)
```python
user = User.objects.get(username='admin')
user_tasks = user.tasks.all()  # Because we set related_name='tasks'

# Filter user's tasks
incomplete = user.tasks.filter(completed=False)

# Count user's tasks
count = user.tasks.count()
```

### Filter across relationships
```python
# Get tasks by username
Task.objects.filter(user__username='admin')

# Get tasks by user email
Task.objects.filter(user__email='admin@example.com')

# Get users who have incomplete tasks
User.objects.filter(tasks__completed=False).distinct()
```

**Double underscore (`__`) is key:**
- `user__username` means "go through the user relationship, then get username"
- This is called "spanning relationships"

---

## Ordering

```python
# Newest first (descending)
Task.objects.order_by('-created_at')

# Oldest first (ascending)
Task.objects.order_by('created_at')

# Multiple fields
Task.objects.order_by('completed', '-created_at')
# Incomplete first, then by newest

# Reverse order
Task.objects.order_by('-created_at').reverse()
```

---

## Limiting Results

```python
# First 5 tasks
Task.objects.all()[:5]

# Tasks 5-10
Task.objects.all()[5:10]

# Get one task (first)
task = Task.objects.filter(completed=False).first()

# Get one task (last)
task = Task.objects.filter(completed=False).last()
```

---

## Combining Queries (AND, OR, NOT)

### AND (default)
```python
# These are the same
Task.objects.filter(completed=False, user=user)
Task.objects.filter(completed=False).filter(user=user)
```

### OR
```python
from django.db.models import Q

# Tasks that are completed OR have "urgent" in title
Task.objects.filter(Q(completed=True) | Q(title__icontains="urgent"))
```

### NOT
```python
from django.db.models import Q

# Tasks that are NOT completed
Task.objects.filter(~Q(completed=True))
# Same as:
Task.objects.exclude(completed=True)
```

### Complex queries
```python
from django.db.models import Q

# (completed=True AND user=user) OR title contains "urgent"
Task.objects.filter(
    (Q(completed=True) & Q(user=user)) | Q(title__icontains="urgent")
)
```

---

## Aggregation (Count, Sum, Avg, etc.)

```python
from django.db.models import Count, Avg, Min, Max

# Count tasks per user
User.objects.annotate(task_count=Count('tasks'))

# Users with more than 5 tasks
User.objects.annotate(task_count=Count('tasks')).filter(task_count__gt=5)

# Aggregate across all tasks
Task.objects.aggregate(total=Count('id'))
# Returns: {'total': 42}
```

---

## Common Patterns for Task Manager

### Get all incomplete tasks for a user
```python
incomplete = Task.objects.filter(user=user, completed=False)
```

### Mark all user's tasks as complete
```python
user.tasks.update(completed=True)
```

### Get tasks created today
```python
from datetime import date
today_tasks = Task.objects.filter(created_at__date=date.today())
```

### Get tasks created this week
```python
from datetime import datetime, timedelta
week_ago = datetime.now() - timedelta(days=7)
recent = Task.objects.filter(created_at__gte=week_ago)
```

### Delete all completed tasks
```python
Task.objects.filter(completed=True).delete()
```

### Search tasks
```python
search_term = "django"
results = Task.objects.filter(
    Q(title__icontains=search_term) | Q(description__icontains=search_term)
)
```

---

## Debugging Queries

### See the SQL Django generates
```python
queryset = Task.objects.filter(completed=False)
print(queryset.query)
# Outputs the SQL query
```

### See number of database hits
```python
from django.db import connection

Task.objects.all()
print(len(connection.queries))  # Shows number of queries
print(connection.queries)  # Shows actual SQL
```

---

## Best Practices

### ✅ DO:
```python
# Use filter() for multiple results
tasks = Task.objects.filter(completed=False)

# Use get() for single result when you're sure it exists
task = Task.objects.get(id=1)

# Use exists() to check if something exists
if Task.objects.filter(user=user).exists():
    print("User has tasks")

# Use select_related() for ForeignKey to reduce queries
tasks = Task.objects.select_related('user').all()
# Gets tasks AND users in one query instead of N+1
```

### ❌ DON'T:
```python
# Don't use get() when multiple results possible
task = Task.objects.get(completed=False)  # ERROR if multiple tasks!

# Don't use all() then filter in Python
tasks = [t for t in Task.objects.all() if t.completed]  # SLOW!
# Use:
tasks = Task.objects.filter(completed=True)  # FAST!

# Don't iterate if you just need count
count = len(Task.objects.all())  # SLOW - loads all into memory
# Use:
count = Task.objects.count()  # FAST - COUNT(*) query
```

---

## Practice Exercises

Try these in `python manage.py shell`:

1. Create 3 tasks for the admin user
2. Get all incomplete tasks
3. Mark the first task as complete
4. Find all tasks with "Django" in the title
5. Delete all completed tasks
6. Count how many tasks the admin user has
7. Get the most recently created task
8. Create a task with no description (use blank=True)

---

## Remember:

- **QuerySets are lazy** - they don't hit the database until you evaluate them
- **Chaining is powerful** - `filter().filter().order_by()`
- **Double underscores** - Used for lookups (`__contains`) and relationships (`user__username`)
- **Use the shell** - `python manage.py shell` is great for experimenting

**Next:** Learn about Views and Templates to create a web interface for your tasks!
