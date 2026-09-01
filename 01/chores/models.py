from django.db import models


class Task(models.Model):
    description = models.CharField(max_length=500)
    assignee = models.CharField(max_length=100)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} — {self.assignee}"
