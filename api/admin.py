from django.contrib import admin
from .models import SalonUser, Service, Appointment,Expense,Review
from .models import Inventory, WalletTransaction, Wallet


# ===========================
# Salon User
# ===========================

@admin.register(SalonUser)
class SalonUserAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "phone",
        "gender",
        "is_verified",
        "is_admin",
        "created_at",

    )

    fields = (
        "user",
        "full_name",
        "phone",
        "age",
        "gender",
        "profile_image",
        "is_verified",
        "is_admin",
    )

    search_fields = (
        "full_name",
        "phone",
        "user__email",
    )

    list_filter = (
        "gender",
        "is_verified",
        "is_admin",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20


# ===========================
# Services
# ===========================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "service_name",
        "duration",
        "price",
        "service_charge",
    )

    search_fields = (
        "service_name",
    )

    ordering = (
        "service_name",
    )

    list_per_page = 20


# ===========================
# Appointment
# ===========================

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer_name",
        "customer_phone",
        "appointment_date",
        "appointment_time",
        "appointment_end_time",
        "status",
        "payment_status",
        "grand_total",
        "show_services",
    )

    readonly_fields = (
        "show_services",
        "appointment_end_time",
        "total_price",
        "total_service_charge",
        "gst",
        "grand_total",
    )

    fields = (
        "user",
        "customer_name",
        "customer_phone",
        "customer_email",
        "show_services",
        "appointment_date",
        "appointment_time",
        "appointment_end_time",
        "total_price",
        "total_service_charge",
        "gst",
        "grand_total",
        "payment_status",
        "status",
        "notes",
    )

    # Search
    search_fields = (
        "customer_name",
        "customer_phone",
        "customer_email",
        "user__email",
    )

    # Filters (Right Side)
    list_filter = (
        "appointment_date",
        "status",
        "payment_status",
    )

    # Date then Time
    ordering = (
        "-appointment_date",
        "appointment_time",
    )

    # Records per page
    list_per_page = 20

    # Date Navigation
    date_hierarchy = "appointment_date"

    def show_services(self, obj):
        return ", ".join(
            service.service_name
            for service in obj.services.all()
        )

    show_services.short_description = "Selected Services"


from .models import AboutSalon


@admin.register(AboutSalon)
class AboutSalonAdmin(admin.ModelAdmin):

    list_display = (
        "salon_name",
        "phone",
        "updated_at"
    )




    # ===========================
# Expense
# ===========================

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "expense_type",
        "title",
        "amount",
        "expense_date",
        "created_at",
    )

    fields = (
        "expense_type",
        "title",
        "amount",
        "description",
        "expense_date",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "expense_type",
        "expense_date",
    )

    ordering = (
        "-expense_date",
        "-created_at",
    )

    list_per_page = 20

    date_hierarchy = "expense_date"

# ===========================
# Inventory
# ===========================
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product_name",
        "stock_quantity",
        "minimum_stock",
        "updated_at",
    )

    search_fields = (
        "product_name",
    )

    list_filter = (
        "updated_at",
    )

    ordering = (
        "product_name",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "appointment",
        "rating",
        "created_at",
    )

    search_fields = (
        "user__full_name",
        "review",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    ordering = (
        "-created_at",
    )



# ===========================
# Wallet Transactions
# ===========================

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "amount",
        "transaction_type",
        "payment_method",
        "status",
        "payment_id",
        "created_at",
    )

    search_fields = (
        "user__full_name",
        "payment_id",
        "reference_id",
    )

    list_filter = (
        "transaction_type",
        "payment_method",
        "status",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "payment_id",
        "reference_id",
        "created_at",
    )





# ===========================
# Wallet
# ===========================

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "balance",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__full_name",
        "user__phone",
        "user__user__email",
    )

    ordering = (
        "-updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )