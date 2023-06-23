from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = "expenses"
urlpatterns = [
    path("", views.index, name="index"),
    path("expenses/new", views.new, name="new"),
    path("expenses/<int:id>/edit", views.edit, name="edit"),
    path("expenses/<int:id>/delete", views.delete, name="delete"),
    path("expenses/search", csrf_exempt(views.search), name="search"),
    path(
        "expense-category-summary",
        views.expense_category_summary,
        name="expense-category-summary",
    ),
    path("stats", views.stats, name="stats"),
]
