from django.urls import path

from .views import PriceEstimateView, ToolsIndexView


app_name = "tools"

urlpatterns = [
    path(
        "precio-de-pasajes-en-micro/",
        PriceEstimateView.as_view(),
        name="price-estimate",
    ),
    path("", ToolsIndexView.as_view(), name="tools-index"),
]
