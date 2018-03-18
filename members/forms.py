# django
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

# local
from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2',
                  'first_name', 'middle_name', 'last_name',
                  'street_and_number', 'zip_code', 'city',
                  'phone', 'birthday')

    def save(self, commit=True):
        user = super().save(commit=True)
        members_group, _new = Group.objects.get_or_create(name='members')
        members_group.user_set.add(user)
        return user
