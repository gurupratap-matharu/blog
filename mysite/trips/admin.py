from django.contrib import admin

from trips.models import Location


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
