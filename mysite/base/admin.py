from django.contrib import admin

from base.models import Country, Person, StandardPage


admin.site.empty_value_display = "(None)"
admin.site.site_title = "Ventanita"
admin.site.site_header = "Ventanita Admin Portal"
admin.site.index_title = "Amor Fati"


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(StandardPage)
class StandardPageAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass
