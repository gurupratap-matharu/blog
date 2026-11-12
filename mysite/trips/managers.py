from django.db import models
from django.db.models import QuerySet


class StopManager(models.Manager["Stop"]):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class CompanyManager(models.Manager["Company"]):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class RouteManager(models.Manager["Route"]):
    def get_by_natural_key(self, code):
        return self.get(code=code)

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        qs = qs.select_related("origin", "destination")
        return qs


class TripManager(models.Manager["Trip"]):
    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        qs = qs.select_related("route", "company")
        return qs
