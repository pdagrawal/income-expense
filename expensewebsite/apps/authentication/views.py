import json
from collections.abc import Callable, Iterable, Mapping
from threading import Thread
from typing import Any

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
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


class EmailThread(Thread):
    def __init__(self, email):
        self.email = email
        Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


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
                EmailThread(email_sender).start()
                messages.success(
                    request, "Account successfully created! Please verify before login!"
                )
                return render(request, "authentication/login.html")

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

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(
                        request, "Welcome, " + username + " You are now logged in!"
                    )
                    return redirect("expenses:index")
                else:
                    messages.error(
                        request, "Account is not active, please check your email!"
                    )
            else:
                messages.error(request, "Invalid credentials, try again!")
        else:
            messages.error(request, "Please provide username and password!")
        return render(request, "authentication/login.html")


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, "authentication/request-reset-password.html")

    def post(self, request):
        email = request.POST["email"]
        if not validate_email(email):
            context = {"values": request.POST}
            messages.error(request, "Please provide a valid email!")
            return render(
                request, "authentication/request-reset-password.html", context
            )
        else:
            domain = get_current_site(request).domain
            users = User.objects.filter(email=email)
            if users.exists():
                email_contents = {
                    "user": users[0],
                    "domain": domain,
                    "uid": urlsafe_base64_encode(force_bytes(users[0].pk)),
                    "token": PasswordResetTokenGenerator().make_token(users[0]),
                }
                link = reverse(
                    "reset-pasword",
                    kwargs={
                        "uidb64": email_contents["uid"],
                        "token": email_contents["token"],
                    },
                )
                email_subject = "Password Reset Instructions"
                reset_url = "http://" + domain + link
                email_sender = EmailMessage(
                    email_subject,
                    "Hi there, Please click the link below to reset your password\n"
                    + reset_url,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                EmailThread(email_sender).start()
            messages.success(
                request, "Reset password link sent! Please check your email!"
            )
            return render(request, "authentication/request-reset-password.html")


class PasswordReset(View):
    def get(self, request, uidb64, token):
        context = {"uidb64": uidb64, "token": token}
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(
                    request, "Password reset link is invalid! Please request a new one."
                )
                return render(request, "authentication/request-reset-password.html")
        except Exception as e:
            pass
        return render(request, "authentication/set-new-password.html", context)

    def post(self, request, uidb64, token):
        context = {"uidb64": uidb64, "token": token}
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return render(request, "authentication/set-new-password.html", context)

        if len(password) < 6 or len(confirm_password) < 6:
            messages.error(request, "Password is too short")
            return render(request, "authentication/set-new-password.html", context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(
                request,
                "Password reset successfully. You can login with the new password.",
            )
            return redirect("login")
        except Exception as e:
            messages.info(request, "Something went wrong! Please try again.")
            return render(request, "authentication/set-new-password.html", context)
