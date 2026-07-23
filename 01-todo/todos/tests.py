from django.test import TestCase


class TodoListTests(TestCase):
    """Tests for the TODO list page."""

    def test_home_page_shows_empty_list(self):
        """The home page explains when no TODOs exist."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No TODOs yet.")
