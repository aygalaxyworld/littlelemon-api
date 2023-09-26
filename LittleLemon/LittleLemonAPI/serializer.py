from .models import Category, MenuItem, Order, OrderItem, Cart
from rest_framework import serializers
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "category", "featured"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class MenuItemTitleField(serializers.CharField):
    queryset = MenuItem.objects.all()

    def to_internal_value(self, data):
        try:
            # Attempt to find a MenuItem by title
            menuitem = MenuItem.objects.get(title=data)
            return menuitem
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid menuitem title."
            )  # Display the title in the dropdown


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    menuitem = MenuItemTitleField()
    unit_price = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = ["user", "menuitem", "quantity", "unit_price", "price"]
        extra_kwargs = {"quantity": {"min_value": 1}}

    def get_unit_price(self, obj):
        return obj.menuitem.price

    def get_price(self, obj):
        # Calculate the price based on unit price and quantity
        return obj.unit_price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    date = serializers.DateField(read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)
    status = serializers.BooleanField()

    class Meta:
        model = Order
        fields = ["user", "delivery_crew", "status", "total", "date"]


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    menuitem = serializers.StringRelatedField(read_only=True)
    quantity = serializers.StringRelatedField(read_only=True)
    unit_price = serializers.StringRelatedField(read_only=True)
    price = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["order", "menuitem", "quantity", "unit_price", "price"]

    def get_status_display(self, obj):
        return "Out for Delivery" if obj.status == False else "Delivered"
