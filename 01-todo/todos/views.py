from django.shortcuts import render


def home(request):
    """Display the TODO list."""
    return render(request, "todos/home.html")
