from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


# ==========================
# USER PROFILE
# ==========================


class SalonUser(models.Model):

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=15,
        unique=True
    )

    age = models.PositiveIntegerField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    profile_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
        default="profile/default.png"
    )

    is_verified = models.BooleanField(default=True)

    # ✅ Admin Login ke liye
    is_admin = models.BooleanField(default=False)

   

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
# ==========================
# SERVICES
# ==========================

class Service(models.Model):

    service_name = models.CharField(max_length=100)

    description = models.TextField()

    duration = models.CharField(max_length=50)

    price = models.FloatField()

    service_charge = models.FloatField(default=0)

    image = models.ImageField(
        upload_to="services/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.service_name


# ==========================
# APPOINTMENT
# ==========================

class Appointment(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    services = models.ManyToManyField(
        Service,
        related_name="appointments"
    )

    # Customer Details
    customer_name = models.CharField(max_length=100)

    customer_phone = models.CharField(max_length=15)

    customer_email = models.EmailField()

    notes = models.TextField(
        blank=True,
        null=True
    )

    # Booking Details
    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    appointment_end_time = models.TimeField(null=True, blank=True)

    # Billing
    total_price = models.FloatField(default=0)

    total_service_charge = models.FloatField(default=0)

    gst = models.FloatField(default=0)

    grand_total = models.FloatField(default=0)

    # Razorpay
    razorpay_order_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_name} | {self.appointment_date} | {self.appointment_time}"


# ==========================
# TIME SLOT
# ==========================

class TimeSlot(models.Model):

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_booked = models.BooleanField(default=False)

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.date} | {self.start_time} - {self.end_time}"


# ==========================
# ABOUT SALON INFORMATION
# ==========================

class AboutSalon(models.Model):

    salon_name = models.CharField(
        max_length=100
    )

    logo = models.ImageField(
        upload_to="about/",
        blank=True,
        null=True
    )

    tagline = models.CharField(
        max_length=200
    )

    about_description = models.TextField()


    owner_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )


    experience = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )


    address = models.TextField()


    phone = models.CharField(
        max_length=15
    )


    email = models.EmailField()


    hair_services = models.TextField(
        blank=True,
        null=True
    )


    skin_services = models.TextField(
        blank=True,
        null=True
    )


    beauty_services = models.TextField(
        blank=True,
        null=True
    )


    why_choose_us = models.TextField(
        blank=True,
        null=True
    )


    app_version = models.CharField(
        max_length=20,
        default="1.0.0"
    )


    developer_name = models.CharField(
        max_length=100,
        default="Glowora Team"
    )


    instagram_link = models.URLField(
        blank=True,
        null=True
    )


    facebook_link = models.URLField(
        blank=True,
        null=True
    )


    website_link = models.URLField(
        blank=True,
        null=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        return self.salon_name













# ==========================
# EXPENSE
# ==========================

class Expense(models.Model):

    EXPENSE_TYPES = [
        ("Staff Salary", "Staff Salary"),
        ("Product Purchase", "Product Purchase"),
        ("Electricity & Utilities", "Electricity & Utilities"),
        ("Other Expenses", "Other Expenses"),
    ]

    expense_type = models.CharField(
        max_length=50,
        choices=EXPENSE_TYPES
    )

    title = models.CharField(
        max_length=150
    )

    amount = models.FloatField()

    description = models.TextField(
        blank=True,
        null=True
    )

    expense_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.expense_type} - ₹{self.amount}"



# ==========================
# INVENTORY STATUS
# ==========================

class Inventory(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["stock_quantity"]

    def __str__(self):
        return self.product_name


class Review(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        SalonUser,
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    review = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name


class WalletTransaction(models.Model):

    TRANSACTION_TYPES = [
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
    ]

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("PENDING", "Pending"),
        ("FAILED", "Failed"),
    ]

    PAYMENT_METHODS = [
        ("RAZORPAY", "Razorpay"),
        ("WALLET", "Wallet"),
        ("REFUND", "Refund"),
    ]

    user = models.ForeignKey(
        SalonUser,
        on_delete=models.CASCADE,
        related_name="wallet_transactions"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    payment_id = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    reference_id = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="SUCCESS"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.transaction_type} - ₹{self.amount}"



# ==========================
# USER WALLET
# ==========================


class Wallet(models.Model):

    user = models.OneToOneField(
        SalonUser,
        on_delete=models.CASCADE,
        related_name="wallet"
    )


    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        return (
            self.user.full_name
            + " - ₹"
            + str(self.balance)
        )


# ==========================
# AUTO CREATE USER WALLET
# ==========================


from django.db.models.signals import post_save
from django.dispatch import receiver



@receiver(
    post_save,
    sender=SalonUser
)
def create_wallet(
        sender,
        instance,
        created,
        **kwargs
):

    if created:

        Wallet.objects.create(
            user=instance
        )