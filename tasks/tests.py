from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task
from .serializers import TaskSerializer


# ===========================================================================
# CHALLENGE 1: Unit Test
# Tests a single piece in isolation — no API calls, no HTTP, just Python.
# ===========================================================================

class TaskModelUnitTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')

    def test_str_returns_title(self):
        """The __str__ method should return the task title."""
        task = Task.objects.create(user=self.user, title='Buy groceries')
        self.assertEqual(str(task), 'Buy groceries')

    def test_default_completed_is_false(self):
        """New tasks should not be completed by default."""
        task = Task.objects.create(user=self.user, title='New task')
        self.assertFalse(task.completed)

    def test_ordering_is_newest_first(self):
        """Tasks should be ordered by created_at descending."""
        task1 = Task.objects.create(user=self.user, title='First')
        task2 = Task.objects.create(user=self.user, title='Second')
        tasks = list(Task.objects.filter(user=self.user))
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)


# ===========================================================================
# CHALLENGE 2: Integration Test (calling the API)
# Hits the real endpoint through the full Django stack.
# ===========================================================================

class TaskAPIIntegrationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.client.force_authenticate(user=self.user)

    def test_full_crud_lifecycle(self):
        """Create, read, update, and delete a task through the API."""
        # Create
        response = self.client.post('/api/tasks/', {'title': 'Test task'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task_id = response.data['id']

        # Read
        response = self.client.get(f'/api/tasks/{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test task')

        # Update
        response = self.client.patch(
            f'/api/tasks/{task_id}/', {'completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['completed'])

        # Delete
        response = self.client.delete(f'/api/tasks/{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's gone
        response = self.client.get(f'/api/tasks/{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ===========================================================================
# CHALLENGE 3: Permission Check Test
# Verifies that unauthorized users get blocked.
# ===========================================================================

class TaskPermissionTest(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')

    def test_unauthenticated_user_cannot_access(self):
        """No login = no access. 403."""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_see_other_users_tasks(self):
        """Alice's tasks should be invisible to Bob."""
        self.client.force_authenticate(user=self.user1)
        self.client.post('/api/tasks/', {'title': 'Alice secret task'})

        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_user_cannot_modify_other_users_task(self):
        """Bob should not be able to update Alice's task."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/tasks/', {'title': 'Alice task'})
        task_id = response.data['id']

        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(
            f'/api/tasks/{task_id}/', {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_other_users_task(self):
        """Bob should not be able to delete Alice's task."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/tasks/', {'title': 'Alice task'})
        task_id = response.data['id']

        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/tasks/{task_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ===========================================================================
# CHALLENGE 4: Serializer Method Field Test
# Verifies that computed values are correct in the API response.
# ===========================================================================

class SerializerMethodFieldTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.client.force_authenticate(user=self.user)

    def test_time_since_created_appears_in_response(self):
        """The computed time_since_created field should be in the response."""
        response = self.client.post('/api/tasks/', {'title': 'Test'})
        self.assertIn('time_since_created', response.data)

    def test_time_since_created_shows_minutes_for_new_task(self):
        """A just-created task should show '0m ago'."""
        response = self.client.post('/api/tasks/', {'title': 'Fresh task'})
        self.assertEqual(response.data['time_since_created'], '0m ago')

    def test_time_since_created_shows_days_for_old_task(self):
        """A task created 3 days ago should show '3d ago'."""
        from django.utils import timezone
        from datetime import timedelta

        task = Task.objects.create(user=self.user, title='Old task')
        task.created_at = timezone.now() - timedelta(days=3)
        task.save(update_fields=['created_at'])

        serializer = TaskSerializer(task)
        self.assertEqual(serializer.data['time_since_created'], '3d ago')


# ===========================================================================
# CHALLENGE 5: Pagination Test
# Verifies pagination behavior when many records exist.
# ===========================================================================

class PaginationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.client.force_authenticate(user=self.user)
        for i in range(25):
            Task.objects.create(user=self.user, title=f'Task {i}')

    def test_first_page_has_10_results(self):
        """With PAGE_SIZE=10, the first page should have 10 tasks."""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_response_includes_count(self):
        """Paginated response should include the total count."""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.data['count'], 25)

    def test_second_page_has_10_results(self):
        """The second page should also have 10 tasks."""
        response = self.client.get('/api/tasks/?page=2')
        self.assertEqual(len(response.data['results']), 10)

    def test_third_page_has_remaining_results(self):
        """The third page should have the remaining 5 tasks."""
        response = self.client.get('/api/tasks/?page=3')
        self.assertEqual(len(response.data['results']), 5)

    def test_next_link_present_on_first_page(self):
        """The first page should have a 'next' link."""
        response = self.client.get('/api/tasks/')
        self.assertIsNotNone(response.data['next'])

    def test_next_link_absent_on_last_page(self):
        """The last page should have no 'next' link."""
        response = self.client.get('/api/tasks/?page=3')
        self.assertIsNone(response.data['next'])


# ===========================================================================
# CHALLENGE 6: Mock External Service Test
# Fakes an outside API call and asserts behavior based on the response.
# ===========================================================================

class DashboardMockTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.client.force_authenticate(user=self.user)

    @patch('tasks.views.get_motivational_quote')
    def test_dashboard_returns_quote_and_task_count(self, mock_quote):
        """Dashboard should return the mocked quote and correct task count."""
        mock_quote.return_value = "You are tremendous."

        Task.objects.create(user=self.user, title='Task 1')
        Task.objects.create(user=self.user, title='Task 2')

        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_count'], 2)
        self.assertEqual(response.data['quote'], "You are tremendous.")
        mock_quote.assert_called_once()

    @patch('tasks.views.get_motivational_quote')
    def test_dashboard_with_no_tasks(self, mock_quote):
        """Dashboard should show 0 tasks for a new user."""
        mock_quote.return_value = "Get to work."

        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.data['task_count'], 0)
        self.assertEqual(response.data['quote'], "Get to work.")

    def test_dashboard_requires_authentication(self):
        """Dashboard should block unauthenticated users."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ===========================================================================
# CHALLENGE 7: Parameterized Test
# One test that runs with many different inputs — valid and invalid.
# ===========================================================================

class ParameterizedTaskCreationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.client.force_authenticate(user=self.user)

    def test_valid_and_invalid_payloads(self):
        """Test various payloads and their expected outcomes."""
        test_cases = [
            # (payload, expected_status, description)
            (
                {'title': 'Valid task'},
                status.HTTP_201_CREATED,
                'Simple valid task',
            ),
            (
                {'title': 'Full task', 'description': 'With details', 'completed': True},
                status.HTTP_201_CREATED,
                'Valid task with all fields',
            ),
            (
                {'title': ''},
                status.HTTP_400_BAD_REQUEST,
                'Empty title should fail',
            ),
            (
                {},
                status.HTTP_400_BAD_REQUEST,
                'Missing title should fail',
            ),
            (
                {'title': 'x' * 201},
                status.HTTP_400_BAD_REQUEST,
                'Title over max_length should fail',
            ),
            (
                {'title': 'Bool test', 'completed': 'not_a_boolean'},
                status.HTTP_400_BAD_REQUEST,
                'Invalid boolean for completed should fail',
            ),
        ]

        for payload, expected_status, description in test_cases:
            with self.subTest(description=description):
                response = self.client.post('/api/tasks/', payload, format='json')
                self.assertEqual(
                    response.status_code, expected_status,
                    f"Failed: {description} — got {response.status_code}, "
                    f"expected {expected_status}"
                )
