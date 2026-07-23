from django.db import models


class Todo(models.Model):
    """A task that can be completed by a due date."""

    title = models.CharField(max_length=200)
    due_date = models.DateField()
    resolved = models.BooleanField(default=False)

    def __str__(self):
        """Return the TODO title."""
        return self.title
