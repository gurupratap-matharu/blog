from collections import Counter

from django.db import models
from django.db.models import QuerySet
from django.utils import timezone


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

    def get_price_distribution(self, obj) -> list[tuple]:
        # this might take non active trips!
        # for now only taking price_a
        qs = obj.trips.values_list("price_a", flat=True)
        c = Counter(qs)
        total = c.total()
        data = []
        for k, v in c.most_common():
            pct = round(100 * v / total)
            data.append((k, v, pct))
        return data

    def get_departure_distribution(self, obj):
        bins = [
            ("Madrugada 12am-6am", 0, 6),
            ("Mañana 6am-12pm", 6, 12),
            ("Tarde 12pm-6pm", 12, 18),
            ("Noche 6pm-12am", 18, 24),
        ]
        # used for final sort
        keys = [x[0] for x in bins]

        counts = Counter({label: 0 for label, _, _ in bins})
        qs = obj.trips.values_list("departure", flat=True)

        for departure in qs:
            local_departure = timezone.localtime(departure)
            hour = local_departure.hour

            for label, start, end in bins:
                if start <= hour < end:
                    counts[label] += 1
                    break
        data = []
        total = counts.total()
        for k, v in counts.most_common():
            pct = round(100 * v / total)
            data.append((k, v, pct))

        data = sorted(data, key=lambda x: keys.index(x[0]))
        return data


class TripManager(models.Manager["Trip"]):
    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        qs = qs.select_related("route", "company")
        return qs
