from django.urls import path

from .views import (
    OrderView,
    PaymentSuccessView,
    PaymentView,
    SeatsView,
    TripDetailView,
    TripSearchView,
)

app_name = "trips"

urlpatterns = [
    path("", TripSearchView.as_view(), name="trip-search"),
    path("<int:service_id>/stops/", TripDetailView.as_view(), name="trip-detail"),
    path("<int:service_id>/seats/", SeatsView.as_view(), name="seats"),
    path("order/", OrderView.as_view(), name="order"),
    path("payment/", PaymentView.as_view(), name="payment"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
]
