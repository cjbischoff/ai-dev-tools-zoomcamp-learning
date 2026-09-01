from django.shortcuts import get_object_or_404, redirect, render

from .models import Task


def task_list(request):
    tasks = Task.objects.all().order_by("-created_at")
    grouped = {}
    for task in tasks:
        grouped.setdefault(task.assignee, []).append(task)
    return render(request, "chores/task_list.html", {"grouped": grouped})


def create_task(request):
    if request.method == "POST":
        description = request.POST.get("description", "").strip()
        assignee = request.POST.get("assignee", "").strip()
        if description and assignee:
            Task.objects.create(description=description, assignee=assignee)
    return redirect("task_list")


def mark_done(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        task.is_done = True
        task.save()
    return redirect("task_list")
