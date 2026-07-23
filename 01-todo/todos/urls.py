from django.urls import path

from . import views

app_name = "todos"

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:pk>/edit/", views.edit_todo, name="edit"),
    path("<int:pk>/resolve/", views.resolve_todo, name="resolve"),
    path("<int:pk>/delete/", views.delete_todo, name="delete"),
]
