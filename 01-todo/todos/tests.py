from datetime import date

from django.test import TestCase

from .models import Todo


class TodoListTests(TestCase):
    """Tests for the TODO list page."""

    def test_home_page_shows_empty_list(self):
        """The home page explains when no TODOs exist."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No TODOs yet.")

    def test_create_todo_with_due_date(self):
        """Submitting the form creates and displays a TODO."""
        response = self.client.post(
            "/",
            {"title": "Finish homework", "due_date": "2026-09-07"},
        )

        self.assertRedirects(response, "/")
        response = self.client.get("/")
        self.assertContains(response, "Finish homework")
        self.assertContains(response, "Sept. 7, 2026")

    def test_edit_todo(self):
        """Submitting the edit form updates a TODO."""
        todo = Todo.objects.create(
            title="Draft homework",
            due_date=date(2026, 9, 7),
        )

        response = self.client.post(
            f"/{todo.pk}/edit/",
            {"title": "Finish homework", "due_date": "2026-09-08"},
        )

        self.assertRedirects(response, "/")
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Finish homework")
        self.assertEqual(todo.due_date, date(2026, 9, 8))

    def test_resolve_todo(self):
        """Resolving a TODO marks it complete."""
        todo = Todo.objects.create(
            title="Finish homework",
            due_date=date(2026, 9, 7),
        )

        response = self.client.post(f"/{todo.pk}/resolve/")

        self.assertRedirects(response, "/")
        todo.refresh_from_db()
        self.assertTrue(todo.resolved)

    def test_delete_todo(self):
        """Deleting a TODO removes it from the list."""
        todo = Todo.objects.create(
            title="Remove this task",
            due_date=date(2026, 9, 7),
        )

        response = self.client.post(f"/{todo.pk}/delete/")

        self.assertRedirects(response, "/")
        self.assertFalse(Todo.objects.filter(pk=todo.pk).exists())
