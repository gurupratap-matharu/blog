from django.urls import path

from .views import (
    OrderCancelView,
    OrderCreateView,
    OrderSearchView,
    TicketsView,
)


app_name = "orders"

urlpatterns = [
    path("create/", OrderCreateView.as_view(), name="order-create"),
    path("search/", OrderSearchView.as_view(), name="order-search"),
    path("<uuid:id>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("tickets/", TicketsView.as_view(), name="tickets"),
]
