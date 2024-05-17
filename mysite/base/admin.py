from django.contrib import admin

from base.models import Country, Person, StandardPage


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(StandardPage)
class StandardPageAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
