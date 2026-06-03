from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""
    list_display = ('title', 'user', 'completed', 'created_at')
    list_filter = ('completed', 'created_at', 'user')
    search_fields = ('title', 'description')
    list_editable = ('completed',)  # Edit completion status directly in list view
