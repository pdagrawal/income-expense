import csv
import datetime
import json

import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from expensewebsite.apps.userpreferences.models import UserPreference

from .models import Category, Expense


@login_required
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {"expenses": expenses, "page_obj": page_obj, "currency": currency}
    return render(request, "expenses/index.html", context)


def search(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchValue", "")
        expenses = (
            Expense.objects.filter(owner=request.user, amount__istartswith=search_str)
            | Expense.objects.filter(owner=request.user, date__icontains=search_str)
            | Expense.objects.filter(
                owner=request.user, description__icontains=search_str
            )
            | Expense.objects.filter(owner=request.user, category__icontains=search_str)
        )
        data = list(expenses.values())
        return JsonResponse(data, safe=False)


@login_required
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


@login_required
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


@login_required
def delete(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense deleted successfully!")
    return redirect("expenses:index")


def expense_category_summary(request):
    today = datetime.date.today()
    six_months_ago = today - datetime.timedelta(days=180)
    total_sums = (
        Expense.objects.filter(
            owner=request.user, date__gte=six_months_ago, date__lte=today
        )
        .values("category")
        .annotate(total=Sum("amount"))
    )
    expense_category_data = {}

    for item in total_sums:
        expense_category_data[item["category"]] = item["total"]

    return JsonResponse({"expense_category_data": expense_category_data}, safe=False)


def stats(request):
    return render(request, "expenses/stats.html")


def export_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="expenses_{str(datetime.datetime.now())}.csv"'
        },
    )
    writer = csv.writer(response)
    # Header
    writer.writerow(["Amount", "Description", "Category", "Date"])
    for expense in Expense.objects.filter(owner=request.user):
        writer.writerow(
            [expense.amount, expense.description, expense.category, expense.date]
        )
    return response


def export_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="expenses_{str(datetime.datetime.now())}.xls"'
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Expenses")
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ["Amount", "Description", "Category", "Date"]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list(
        "amount", "description", "category", "date"
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
