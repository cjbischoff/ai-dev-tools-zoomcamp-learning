from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    """Collect editable TODO fields."""

    class Meta:
        model = Todo
        fields = ["title", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}
