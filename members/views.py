# django
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, ListView
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin

# local
from .forms import CustomUserCreationForm
from .models import User


class Login(LoginView):
    template_name = "members/login.html"


class Logout(LogoutView):
    template_name = "members/login.html"


class Registration(CreateView):
    model = User
    template_name = "members/registration.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('fablog:home')


class MemberListView(PermissionRequiredMixin, ListView):
    permission_required = 'members.view_members'

    template_name = "members/members_listview.html"
    context_object_name = 'members'

    def get_queryset(self):
        return User.members.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
