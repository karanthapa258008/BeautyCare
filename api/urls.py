from django.urls import path
from . import views

urlpatterns = [

    # ================= Authentication =================

    path("send-otp/", views.send_otp),
    path("verify-otp/", views.verify_otp),

    path("create-profile/", views.create_profile),
    path("login/", views.login_user),

    path("forgot-password-send-otp/", views.forgot_password_send_otp),
    path("reset-password/", views.reset_password),

    # ================= Profile =================

    path("get-profile/", views.get_profile),
    path("update-profile/", views.update_profile),

    # ================= Services =================

    path("services/", views.get_services),

    # ================= Appointment =================

    path("create-appointment/", views.create_appointment),


    path("available-slots/", views.available_slots),


    path("create-order/", views.create_order),
    path("verify-payment/", views.verify_payment),


     path("my-bookings/",views.my_bookings,name="my_bookings"),

     path("booking-history/",views.booking_history),
     path("about/",views.get_about_salon),



     path("customer-report/", views.customer_report),
     path("revenue-report/", views.revenue_report),
     path("service-report/", views.service_report),
     path("appointment-report/", views.appointment_report),
     path("payment-report/",views.payment_report),
     path("dashboard-summary/",views.dashboard_summary),
     path("top-customers/",views.top_customers),
     path("top-services/",views.top_services),
     path("monthly-revenue/",views.monthly_revenue),
     path("add-expense/", views.add_expense),
     path("expense-list/", views.expense_list),
     path("expense-summary/", views.expense_summary),
     path("delete-expense/", views.delete_expense),
     path("profit-summary/", views.profit_summary),
     # ==========================
# Inventory API
# ==========================

path("add-inventory/", views.add_inventory),
path("inventory-list/", views.inventory_list),
path("add-stock/", views.add_stock),
path("reduce-stock/", views.reduce_stock),
path("update-inventory/", views.update_inventory),
path("delete-inventory/", views.delete_inventory),
path("inventory-summary/", views.inventory_summary),
path("update-appointment-status/", views.update_appointment_status),
path("can-review/", views.can_review),
path("submit-review/", views.submit_review),
path("my-reviews/", views.my_reviews),
path("service-reviews/", views.service_reviews),
# ================= Wallet =================

path(
    "wallet-balance/",
    views.wallet_balance,
    name="wallet_balance"
),

path(
    "create-wallet-order/",
    views.create_wallet_order,
    name="create_wallet_order"
),

path(
    "verify-wallet-payment/",
    views.verify_wallet_payment,
    name="verify_wallet_payment"
),

path(
    "wallet-history/",
    views.wallet_history,
    name="wallet_history"
),

path(
    "use-wallet-payment/",
    views.use_wallet_payment
),
]