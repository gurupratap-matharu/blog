from django.urls import path

from .views import SearchView, SeatsView, TripDetailView, TripSearchView

app_name = "trips"

urlpatterns = [
    path("", TripSearchView.as_view(), name="trip-search"),
    path("<int:service_id>/stops/", TripDetailView.as_view(), name="trip-detail"),
    path("<int:service_id>/seats/", SeatsView.as_view(), name="seats"),
    path("<slug:origin>/<slug:destination>/", SearchView.as_view(), name="search"),
]
