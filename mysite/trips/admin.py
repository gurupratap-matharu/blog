from typing import ClassVar

from django.contrib import admin, messages
from django.core.management import call_command
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html, format_html_join

from trips.models import Company, Route, Stop, Trip


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin[Company]):
    list_display = ("id", "name", "trips", "red_code", "pink_code", "blue_code", "active")
    list_display_links = ("id", "name")
    list_per_page = 30
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    search_fields = ("id", "name")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Company]:
        qs = super().get_queryset(request)
        qs = qs.annotate(num_trips=Count("services", distinct=True))
        return qs

    def trips(self, obj: Company) -> int:
        return obj.num_trips

    def active(self, obj: Company) -> bool:
        return obj.is_active

    active.boolean = True


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin[Stop]):
    list_display = ("id", "name", "code", "state", "red_code", "pink_code", "blue_code", "is_active")
    list_display_links = ("id", "name")
    list_per_page = 30
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    list_filter = ("kind", "state", "is_active")
    search_fields = ("id", "name", "code")
    _basic_fields = (
        ("name", "slug", "code"),
        ("description", "kind"),
    )
    _geo_fields = (("lat", "lon"), ("address", "city", "state"))
    _extra_fields = (("red_code", "pink_code", "blue_code"), "is_active")
    fieldsets = (
        ("Basic Information", {"fields": _basic_fields}),
        ("Geo", {"fields": _geo_fields}),
        ("Extra", {"fields": _extra_fields}),
    )


class TripInlineAdmin(admin.TabularInline):
    model = Trip
    extra = 0


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin[Route]):
    list_display = (
        "id",
        "name",
        "trips",
        "operators",
        "distance",
        "min_fare",
        "min_time",
        "last_updated",
        "red",
        "blue",
        "pink",
        "map",
        "active",
        "strategy",
        "pull_preference",
    )
    list_display_links = ("id", "name")
    list_filter = ("updated", "strategy", "is_active")
    list_per_page = 30
    list_select_related = ("origin", "destination")
    autocomplete_fields = ("origin", "destination")
    search_fields = ("id", "code", "origin__name", "destination__name")
    inlines = (TripInlineAdmin,)
    actions = ("pull_red", "pull_blue", "pull")

    _basic_fields = (("name", "code"), ("origin", "destination"))
    _extra_fields = (("distance", "co2", "strategy", "pull_preference", "is_active"),)
    _price_duration_fields = (("min_price", "avg_price", "min_duration", "avg_duration"),)
    _departure_fields = (("num_departures", "num_companies"), ("first_departure", "last_departure"))

    fieldsets = (
        ("Basic Information", {"fields": _basic_fields}),
        ("Extra", {"fields": _extra_fields}),
        ("Price & Duration", {"fields": _price_duration_fields}),
        ("Departures", {"fields": _departure_fields}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Route]:
        qs = super().get_queryset(request)
        qs = qs.annotate(num_trips=Count("trips", distinct=True))
        return qs

    def trips(self, obj: Route) -> int:
        return obj.num_trips

    def operators(self, obj: Route) -> int:
        return obj.num_companies or 0

    def min_fare(self, obj: Route) -> str:
        fare = f"{obj.min_price:,.0f}" if obj.min_price else "?"
        return fare

    @admin.display(ordering="min_duration")
    def min_time(self, obj: Route) -> str:
        # converts 5:20:00 -> 5:20
        return str(obj.min_duration)[:-3] if obj.min_duration else "?"

    @admin.display(ordering="updated")
    def last_updated(self, obj: Route) -> str:
        return obj.updated.strftime("%d %b %Y %H:%M:%S")

    def red(self, obj: Route) -> str:
        url = obj.get_red_url()
        return format_html("<a href='{}' target='_blank'>View</a>", url)

    def blue(self, obj: Route) -> str:
        url = obj.get_blue_url()
        return format_html("<a href='{}' target='_blank'>View</a>", url)

    def pink(self, obj: Route) -> str:
        url = obj.get_pink_url()
        return format_html("<a href='{}' target='_blank'>View</a>", url)

    def map(self, obj: Route) -> str:
        url = obj.get_maps_directions_url()
        return format_html("<a href='{}' target='_blank'>See</a>", url)

    def active(self, obj: Route) -> bool:
        return obj.is_active

    active.boolean = True

    @admin.action(description="Pull selected routes from Red")
    def pull_red(self, request: HttpRequest, qs: QuerySet[Route]) -> None:
        ids = [obj.id for obj in qs]
        out = call_command("pull_red", ids)
        self.message_user(request, f"{out} {len(qs)} routes updated.", messages.SUCCESS)

    @admin.action(description="Pull selected routes from Blue")
    def pull_blue(self, request: HttpRequest, qs: QuerySet[Route]) -> None:
        ids = [obj.id for obj in qs]
        out = call_command("pull_blue", ids)
        self.message_user(request, f"{out} {len(qs)} routes updated.", messages.SUCCESS)

    @admin.action(description="Pull selected routes via Preference")
    def pull(self, request: HttpRequest, qs: QuerySet[Route]) -> None:
        blue_qs = qs.filter(pull_preference=Route.PullPreference.BLUE)
        red_qs = qs.filter(pull_preference=Route.PullPreference.RED)
        if blue_qs.exists():
            self.pull_blue(request, blue_qs)
        if red_qs.exists():
            self.pull_red(request, red_qs)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "company", "departs", "arrives", "runtime", "price", "strategy")
    list_per_page = 30
    list_select_related = ("route", "company")
    list_filter = ("strategy", "updated")
    search_fields = ("route__name", "company__name", "route__origin__name", "route__destination__name")

    @admin.display(ordering="departure")
    def departs(self, obj: Trip) -> str:
        return obj.departure.strftime("%d %b %H:%M")

    @admin.display(ordering="arrival")
    def arrives(self, obj: Trip) -> str:
        return obj.arrival.strftime("%d %b %H:%M")

    @admin.display(ordering="duration")
    def runtime(self, obj: Trip) -> str:
        # converts 5:20:00 -> 5:20
        return str(obj.duration)[:-3]

    def price(self, obj: Trip) -> str:
        prices = [(obj.category_a, obj.price_a), (obj.category_b, obj.price_b), (obj.category_c, obj.price_c)]
        prices = [(obj.Category(x[0]).label, x[1]) for x in prices if x[0] and x[1]]
        return format_html_join("\n", "<span>{} {}</span><br>", (prices))
