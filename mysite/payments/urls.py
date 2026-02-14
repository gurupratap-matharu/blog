from django.urls import path

from .views import (
    MercadoPagoView,
    PaymentFailView,
    PaymentPendingView,
    PaymentSuccessView,
    PaymentView,
    mailgun_webhook,
    mercadopago_success,
    mercadopago_webhook,
)


app_name = "payments"

urlpatterns = [
    path("", PaymentView.as_view(), name="home"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("fail/", PaymentFailView.as_view(), name="fail"),
    path("pending/", PaymentPendingView.as_view(), name="pending"),
    path("mercado-pago/", MercadoPagoView.as_view(), name="mercado-pago"),
    path(
        "mercado-pago/success/",
        mercadopago_success,
        name="mercado-pago-success",
    ),
    path(
        "webhooks/mercado-pago/drSndwy4YXkO15Zx1gABbbspSpxOasfx/",
        mercadopago_webhook,
        name="mercado-pago-webhook",
    ),
    path(
        "webhooks/mailgun/EAm4CP6Y3PgO0WfsMJvdFPmWMRWAWbm3/",
        mailgun_webhook,
        name="mailgun-webhook",
    ),
]
