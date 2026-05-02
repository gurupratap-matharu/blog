from django.urls import path

from .views import page_feedback, suggestion


app_name = "base"

urlpatterns = [
    path("page-feedback/", page_feedback, name="page-feedback"),
    path("suggestion/", suggestion, name="suggestion"),
]
