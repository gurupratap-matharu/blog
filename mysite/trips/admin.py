from django.contrib import admin

from trips.models import Location, Stats


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "abbr",
        "city",
        "state",
        "postal_code",
        "country",
        "latitude",
        "longitude",
    )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_per_page = 30


@admin.register(Stats)
class StatsAdmin(admin.ModelAdmin):
    list_display = (
        "origin",
        "destination",
        "price_economy",
        "price_avg",
        "first_departure",
        "last_departure",
        "duration",
        "num_departures",
    )
