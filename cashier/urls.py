# django
from django.urls import path

# local
from . import views

app_name = 'cashier'
urlpatterns = [
    path("<int:pk>/", views.AccountJournalView.as_view(), name="journal"),
    path("cashcount/", views.CashCountCreateView.as_view(), name="new_cash_count")
]
