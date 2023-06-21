from django.urls import path

from . import views

app_name = "expenses"
urlpatterns = [
    path("", views.index, name="index"),
    path("expenses/new", views.new, name="new"),
    path("expenses/<int:id>/edit", views.edit, name="edit"),
    path("expenses/<int:id>/delete", views.delete, name="delete"),
]
