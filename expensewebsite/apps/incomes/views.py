import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render

from expensewebsite.apps.userpreferences.models import UserPreference

from .models import Income, Source


@login_required
def index(request):
    incomes = Income.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {"incomes": incomes, "page_obj": page_obj, "currency": currency}
    return render(request, "incomes/index.html", context)


def search(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchValue", "")
        incomes = (
            Income.objects.filter(owner=request.user, amount__istartswith=search_str)
            | Income.objects.filter(owner=request.user, date__icontains=search_str)
            | Income.objects.filter(
                owner=request.user, description__icontains=search_str
            )
            | Income.objects.filter(owner=request.user, source__icontains=search_str)
        )
        data = list(incomes.values())
        return JsonResponse(data, safe=False)


@login_required
def new(request):
    sources = Source.objects.all()
    context = {"sources": sources, "values": request.POST}
    if request.method == "GET":
        return render(request, "incomes/new.html", context)
    else:
        amount = request.POST["amount"]
        description = request.POST["description"]
        source = request.POST["source"]
        date = request.POST["income_date"]
        if not amount:
            messages.error(request, "Amount is required!")
        if not description:
            messages.error(request, "Description is required!")
        if not amount or not description:
            return render(request, "incomes/new.html", context)
        Income.objects.create(
            owner=request.user,
            amount=amount,
            description=description,
            source=source,
            date=date,
        )
        messages.success(request, "Income saved successfully!")
        return redirect("incomes:index")


@login_required
def edit(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {"values": income, "sources": sources}
    if request.method == "GET":
        return render(request, "incomes/edit.html", context)

    amount = request.POST["amount"]
    description = request.POST["description"]
    source = request.POST["source"]
    date = request.POST["income_date"]
    if not amount:
        messages.error(request, "Amount is required!")
    if not description:
        messages.error(request, "Description is required!")
    if not amount or not description:
        return render(request, "incomes/edit.html", context)

    income.amount = amount
    income.description = description
    income.source = source
    income.date = date
    income.save()
    messages.success(request, "Income updated successfully!")
    return redirect("incomes:index")


@login_required
def delete(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, "Income deleted successfully!")
    return redirect("incomes:index")
