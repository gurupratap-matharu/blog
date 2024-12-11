from django.urls import path

from .views import HelpSearchView

app_name = "help"

urlpatterns = [path("search/", HelpSearchView.as_view(), name="search")]
