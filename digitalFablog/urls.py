"""digitalFablog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from members.views import Login, Logout, Registration

urlpatterns = [
    # admin
    path("admin/", admin.site.urls),
    # landing page
    path("", RedirectView.as_view(url="fablog/")),
    # fablogs
    path("fablog/", include("fablog.urls", namespace="fablog")),
    # members
    path("members/", include("members.urls", namespace="members")),
    # accounts
    path("cashier/", include("cashier.urls", namespace="cashier")),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("registration/", Registration.as_view(), name="registration")
]
