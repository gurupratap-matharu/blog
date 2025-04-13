from django.urls import path

from .views import OrderView, PaymentSuccessView, PaymentView, SeatsView, TripListView

app_name = "trips"

urlpatterns = [
    path("", TripListView.as_view(), name="trip-list"),
    path("seats/", SeatsView.as_view(), name="seats"),
    path("order/", OrderView.as_view(), name="order"),
    path("payment/", PaymentView.as_view(), name="payment"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
]
