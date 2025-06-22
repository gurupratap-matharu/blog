from django.contrib import admin

from trips.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass
