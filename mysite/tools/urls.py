from django.urls import path

from .views import PriceEstimateView

app_name = "tools"

urlpatterns = [
    path(
        "precio-de-pasajes-en-micro/",
        PriceEstimateView.as_view(),
        name="price-estimate",
    ),
]
