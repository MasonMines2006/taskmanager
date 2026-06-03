from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """A task that belongs to a specific user."""

    # Each task belongs to one user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    # Task details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Newest tasks first

    def __str__(self):
        """String representation of the task."""
        return self.title
