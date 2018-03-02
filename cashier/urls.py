from django.urls import path
from . import views
from cashier

app_name = 'fablog'
urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("<int:pk>/", views.FablogUpdateView.as_view(), name="update"),
    path("<int:pk>/booking", views.FablogBookingUpdateView.as_view(), name="booking"),
    path("new/", views.FablogCreateView.as_view(), name="create")
]
