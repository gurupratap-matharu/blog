from django.urls import path

from .views import PaymentFailView, PaymentSuccessView, PaymentView

app_name = "payments"

urlpatterns = [
    path("", PaymentView.as_view(), name="home"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("fail/", PaymentFailView.as_view(), name="fail"),
]
