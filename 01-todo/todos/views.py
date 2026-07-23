from django.shortcuts import redirect, render

from .forms import TodoForm
from .models import Todo


def home(request):
    """Display the TODO list."""
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("todos:home")
    else:
        form = TodoForm()

    return render(
        request,
        "todos/home.html",
        {"form": form, "todos": Todo.objects.all()},
    )
