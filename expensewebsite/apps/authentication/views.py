import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from validate_email import validate_email

from expensewebsite import settings

from .tokens import token_generator


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data["username"]
        if not str(username).isalnum():
            return JsonResponse(
                {
                    "username_error": "username should only contain alphanumeric characters!"
                },
                status=400,
            )
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "username_error": "sorry! username already in use, choose another one!"
                },
                status=409,
            )
        return JsonResponse({"username_valid": True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data["email"]
        if not validate_email(email):
            return JsonResponse(
                {"email_error": "Email is invalid!"},
                status=400,
            )
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"email_error": "sorry! email already in use, choose another one!"},
                status=409,
            )
        return JsonResponse({"email_valid": True})


class RegistrationView(View):
    def get(self, request):
        return render(request, "authentication/register.html")

    def post(self, request):
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        context = {"fieldValues": request.POST}

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password is too short")
                    return render(request, "authentication/register.html", context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                domain = get_current_site(request).domain
                link = reverse(
                    "activate",
                    kwargs={
                        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": token_generator.make_token(user),
                    },
                )
                email_subject = "Activate your account"
                activate_url = "http://" + domain + link
                email_body = (
                    "Hi "
                    + user.username
                    + "Please use this link to verify your account\n"
                    + activate_url
                )
                email_sender = EmailMessage(
                    email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [email]
                )
                email_sender.send(fail_silently=False)
                messages.success(request, "Account successfully created!")
                return render(request, "authentication/register.html")

        return render(request, "authentication/register.html")


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if not token_generator.check_token(user, token):
                return redirect("login" + "?message=" + "User already activated")

            if user.is_active:
                return redirect("login")
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully!")
        except Exception as ex:
            pass
        return redirect("login")


class LoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")
