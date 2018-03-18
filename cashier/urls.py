# django
from django.urls import path

# local
from . import views

app_name = 'cashier'
urlpatterns = [
    path("<int:pk>/", views.AccountBookingListView.as_view(), name="account"),
    path("cashcount/", views.CashCountCreateView.as_view(), name="new_cash_count")
]
