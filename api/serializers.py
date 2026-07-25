from rest_framework import serializers
from .models import Service
from .models import Appointment
from .models import AboutSalon
from .models import Expense
from .models import Inventory
from .models import Review
from .models import WalletTransaction
from django.utils import timezone



class ServiceSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = "__all__"


       

class AboutSalonSerializer(serializers.ModelSerializer):

    class Meta:
        model = AboutSalon
        fields = "__all__"


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = "__all__"



# ==========================
# INVENTORY SERIALIZER
# ==========================

class InventorySerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            "id",
            "product_name",
            "stock_quantity",
            "minimum_stock",
            "updated_at",
            "status",
        ]

    def get_status(self, obj):
        if obj.stock_quantity == 0:
            return "Out Of Stock"
        elif obj.stock_quantity < obj.minimum_stock:
            return "Low Stock"
        return "In Stock"





class ReviewSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="user.full_name",
        read_only=True
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "customer_name",
            "rating",
            "review",
            "created_at",
        ]



class WalletTransactionSerializer(serializers.ModelSerializer):

    type = serializers.CharField(source="transaction_type")

    date = serializers.SerializerMethodField()

    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "amount",
            "type",
            "description",
            "date",
            "status"
        ]

    def get_date(self, obj):
        local_time = timezone.localtime(obj.created_at)
        return local_time.strftime("%d %b %Y %I:%M %p")