from django.urls import path
from members import views

app_name = 'members'

# login and registration views have their urls in the main digitalFablog/url.py

urlpatterns = [
    path("", views.MemberListView.as_view(), name="members_list")
]
