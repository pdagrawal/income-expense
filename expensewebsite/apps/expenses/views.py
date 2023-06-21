from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Category, Expense


@login_required(login_url="/authentication/login")
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    context = {"expenses": expenses}
    return render(request, "expenses/index.html", context)


def new(request):
    categories = Category.objects.all()
    context = {"categories": categories, "values": request.POST}
    if request.method == "GET":
        return render(request, "expenses/new.html", context)
    else:
        amount = request.POST["amount"]
        description = request.POST["description"]
        category = request.POST["category"]
        date = request.POST["expense_date"]
        if not amount:
            messages.error(request, "Amount is required!")
        if not description:
            messages.error(request, "Description is required!")
        if not amount or not description:
            return render(request, "expenses/new.html", context)
        Expense.objects.create(
            owner=request.user,
            amount=amount,
            description=description,
            category=category,
            date=date,
        )
        messages.success(request, "Expense saved successfully!")
        return redirect("expenses:index")


def edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {"values": expense, "categories": categories}
    if request.method == "GET":
        return render(request, "expenses/edit.html", context)

    amount = request.POST["amount"]
    description = request.POST["description"]
    category = request.POST["category"]
    date = request.POST["expense_date"]
    if not amount:
        messages.error(request, "Amount is required!")
    if not description:
        messages.error(request, "Description is required!")
    if not amount or not description:
        return render(request, "expenses/edit.html", context)

    expense.amount = amount
    expense.description = description
    expense.category = category
    expense.date = date
    expense.save()
    messages.success(request, "Expense updated successfully!")
    return redirect("expenses:index")


def delete(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense deleted successfully!")
    return redirect("expenses:index")
