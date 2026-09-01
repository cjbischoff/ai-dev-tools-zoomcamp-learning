from django.test import TestCase

from .models import Task


class TaskModelTests(TestCase):
    def test_create_task(self):
        task = Task.objects.create(description="Wash dishes", assignee="Alice")
        self.assertEqual(task.description, "Wash dishes")
        self.assertEqual(task.assignee, "Alice")
        self.assertFalse(task.is_done)
        self.assertIsNotNone(task.created_at)

    def test_str_representation(self):
        task = Task.objects.create(description="Vacuum", assignee="Bob")
        self.assertEqual(str(task), "Vacuum — Bob")


class TaskListViewTests(TestCase):
    def test_empty_list_shows_no_tasks_message(self):
        response = self.client.get("/")
        self.assertContains(response, "No tasks yet.")

    def test_tasks_are_grouped_by_assignee(self):
        Task.objects.create(description="Wash dishes", assignee="Alice")
        Task.objects.create(description="Vacuum", assignee="Bob")
        Task.objects.create(description="Cook dinner", assignee="Alice")

        response = self.client.get("/")
        self.assertContains(response, "Alice")
        self.assertContains(response, "Bob")
        self.assertContains(response, "Wash dishes")
        self.assertContains(response, "Vacuum")
        self.assertContains(response, "Cook dinner")

    def test_newest_tasks_appear_first_in_group(self):
        Task.objects.create(description="Old task", assignee="Alice")
        Task.objects.create(description="New task", assignee="Alice")

        response = self.client.get("/")
        # Newer task should appear first in the template
        self.assertNotEqual(response.content.find(b"New task"), -1)
        self.assertNotEqual(response.content.find(b"Old task"), -1)


class CreateTaskTests(TestCase):
    def test_create_task_via_post(self):
        response = self.client.post("/create/", {"description": "Mop floor", "assignee": "Charlie"})
        self.assertRedirects(response, "/")
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.get()
        self.assertEqual(task.description, "Mop floor")
        self.assertEqual(task.assignee, "Charlie")

    def test_empty_description_does_not_create_task(self):
        response = self.client.post("/create/", {"description": "", "assignee": "Alice"})
        self.assertRedirects(response, "/")
        self.assertEqual(Task.objects.count(), 0)

    def test_empty_assignee_does_not_create_task(self):
        response = self.client.post("/create/", {"description": "Sweep", "assignee": ""})
        self.assertRedirects(response, "/")
        self.assertEqual(Task.objects.count(), 0)

    def test_created_task_appears_in_list(self):
        self.client.post("/create/", {"description": "Take out trash", "assignee": "Diana"})
        response = self.client.get("/")
        self.assertContains(response, "Take out trash")
        self.assertContains(response, "Diana")


class MarkDoneTests(TestCase):
    def test_mark_task_as_done(self):
        task = Task.objects.create(description="Clean windows", assignee="Eve")
        response = self.client.post(f"/{task.id}/done/")
        self.assertRedirects(response, "/")
        task.refresh_from_db()
        self.assertTrue(task.is_done)

    def test_done_task_shows_strikethrough(self):
        task = Task.objects.create(description="Clean windows", assignee="Eve")
        self.client.post(f"/{task.id}/done/")
        response = self.client.get("/")
        self.assertContains(response, "<s>Clean windows</s>", html=True)

    def test_mark_done_nonexistent_task_returns_404(self):
        response = self.client.post("/999/done/")
        self.assertEqual(response.status_code, 404)

    def test_get_request_to_done_redirects(self):
        task = Task.objects.create(description="Fix shelf", assignee="Frank")
        response = self.client.get(f"/{task.id}/done/")
        self.assertRedirects(response, "/")
        task.refresh_from_db()
        self.assertFalse(task.is_done)
