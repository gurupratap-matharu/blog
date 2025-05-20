from django.contrib import admin

from orders.models import Order, Passenger


class OrderPassengerInline(admin.TabularInline):
    model = Order.passengers.through
    readonly_fields = (
        "order",
        "passenger",
    )
    extra = 0
    classes = ("collapse",)
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "paid", "created_on")
    list_filter = ("paid", "created_on")
    exclude = ("passengers",)
    inlines = [
        OrderPassengerInline,
    ]


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        "name",
        "document_type",
        "document_number",
        "nationality",
        "gender",
        "phone_number",
    )

    def name(self, obj):
        return obj.get_full_name()
