from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    time_since_created = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'created_at',
                  'updated_at', 'time_since_created']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_time_since_created(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        if delta.days > 0:
            return f"{delta.days}d ago"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours}h ago"
        minutes = delta.seconds // 60
        return f"{minutes}m ago"
