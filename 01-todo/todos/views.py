from django.shortcuts import get_object_or_404, redirect, render

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


def edit_todo(request, pk):
    """Edit an existing TODO."""
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect("todos:home")
    else:
        form = TodoForm(instance=todo)

    return render(request, "todos/todo_form.html", {"form": form})
