from django.contrib.auth.views import LoginView, LogoutView


class login(LoginView):
    template_name = "accounts/login.html"


class logout(LogoutView):
    template_name = "accounts/login.html"
