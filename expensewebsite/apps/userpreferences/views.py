import json
import os

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render

from .models import UserPreference


def index(request):
    if UserPreference.objects.filter(user=request.user).exists():
        user_preferences = UserPreference.objects.get(user=request.user)
    else:
        user_preferences = UserPreference.objects.create(user=request.user, currency="")

    if request.method == "POST":
        user_preferences.currency = request.POST["currency"]
        user_preferences.save()
        messages.success(request, "Changes saved!")

    currency_data = []
    filepath = os.path.join(settings.BASE_DIR, "currencies.json")

    with open(filepath, "r") as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({"name": k, "value": v})

    return render(
        request,
        "preferences/index.html",
        {"currencies": currency_data, "user_preferences": user_preferences},
    )
