from django.urls import path

from .views import price_estimate, tools_index


app_name = "tools"

urlpatterns = [
    path(
        "precio-de-pasajes-en-micro/",
        price_estimate,
        name="price-estimate",
    ),
    path("", tools_index, name="tools-index"),
]
