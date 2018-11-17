# django
from django.urls import path

# local
from . import views
from cashier.views import FablogPaymentCreateView

app_name = 'fablog'
urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("<int:pk>/", views.FablogUpdateView.as_view(), name="update"),
    path("<int:pk>/detail", views.FablogDetailView.as_view(), name="detail"),
    path("<int:pk>/payment", FablogPaymentCreateView.as_view(), name="payment"),
    path("new/", views.FablogCreateView.as_view(), name="create")
]
