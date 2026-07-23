from django.urls import path

from . import views

app_name = "todos"

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:pk>/edit/", views.edit_todo, name="edit"),
]
