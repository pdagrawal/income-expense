from django.contrib import admin

from .models import Category, Expense

admin.site.register(Expense)
admin.site.register(Category)
