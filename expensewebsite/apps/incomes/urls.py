from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = "incomes"
urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("<int:id>/edit", views.edit, name="edit"),
    path("<int:id>/delete", views.delete, name="delete"),
    path("search", csrf_exempt(views.search), name="search"),
]
