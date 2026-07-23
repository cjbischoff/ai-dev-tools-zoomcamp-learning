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

    def test_invalid_create_shows_errors_and_creates_nothing(self):
        """Invalid form data is rejected without creating a TODO."""
        response = self.client.post(
            "/",
            {"title": "", "due_date": "not-a-date"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Todo.objects.count(), 0)

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

    def test_edit_page_shows_existing_values(self):
        """The edit form is populated with the current TODO values."""
        todo = Todo.objects.create(
            title="Draft homework",
            due_date=date(2026, 9, 7),
        )

        response = self.client.get(f"/{todo.pk}/edit/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Draft homework")
        self.assertContains(response, 'value="2026-09-07"')

    def test_invalid_edit_preserves_existing_todo(self):
        """Invalid edits display errors without changing the TODO."""
        todo = Todo.objects.create(
            title="Finish homework",
            due_date=date(2026, 9, 7),
        )

        response = self.client.post(
            f"/{todo.pk}/edit/",
            {"title": "", "due_date": "2026-09-08"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Finish homework")
        self.assertEqual(todo.due_date, date(2026, 9, 7))

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

    def test_resolved_todo_is_identified_on_home_page(self):
        """The home page labels completed TODOs as resolved."""
        Todo.objects.create(
            title="Finish homework",
            due_date=date(2026, 9, 7),
            resolved=True,
        )

        response = self.client.get("/")

        self.assertContains(response, "Resolved")
        self.assertNotContains(response, ">Resolve</button>")

    def test_resolve_rejects_get_requests(self):
        """Resolving a TODO requires a POST request."""
        todo = Todo.objects.create(
            title="Finish homework",
            due_date=date(2026, 9, 7),
        )

        response = self.client.get(f"/{todo.pk}/resolve/")

        self.assertEqual(response.status_code, 405)
        todo.refresh_from_db()
        self.assertFalse(todo.resolved)

    def test_delete_todo(self):
        """Deleting a TODO removes it from the list."""
        todo = Todo.objects.create(
            title="Remove this task",
            due_date=date(2026, 9, 7),
        )

        response = self.client.post(f"/{todo.pk}/delete/")

        self.assertRedirects(response, "/")
        self.assertFalse(Todo.objects.filter(pk=todo.pk).exists())

    def test_delete_rejects_get_requests(self):
        """Deleting a TODO requires a POST request."""
        todo = Todo.objects.create(
            title="Keep this task",
            due_date=date(2026, 9, 7),
        )

        response = self.client.get(f"/{todo.pk}/delete/")

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Todo.objects.filter(pk=todo.pk).exists())

    def test_unknown_todo_returns_not_found(self):
        """TODO operations return 404 when the requested TODO is absent."""
        requests = [
            ("get", "/999/edit/"),
            ("post", "/999/resolve/"),
            ("post", "/999/delete/"),
        ]

        for method, path in requests:
            with self.subTest(path=path):
                response = getattr(self.client, method)(path)
                self.assertEqual(response.status_code, 404)

    def test_complete_todo_workflow(self):
        """A TODO can move through its complete user workflow."""
        self.client.post(
            "/",
            {"title": "Draft homework", "due_date": "2026-09-07"},
        )
        todo = Todo.objects.get()

        self.client.post(
            f"/{todo.pk}/edit/",
            {"title": "Finish homework", "due_date": "2026-09-08"},
        )
        self.client.post(f"/{todo.pk}/resolve/")

        response = self.client.get("/")
        self.assertContains(response, "Finish homework")
        self.assertContains(response, "Sept. 8, 2026")
        self.assertContains(response, "Resolved")

        self.client.post(f"/{todo.pk}/delete/")
        response = self.client.get("/")
        self.assertNotContains(response, "Finish homework")
        self.assertContains(response, "No TODOs yet.")
