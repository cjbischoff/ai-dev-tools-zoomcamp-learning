from django.test import TestCase


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
