from rest_framework import serializers
from .models import Category, Product, Inventory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["quantity"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description",
            "price_cents", "currency", "is_active",
            "category", "category_id", "inventory", "image_url"
        ]
