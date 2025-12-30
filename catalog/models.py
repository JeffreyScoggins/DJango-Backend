from django.db import models

# Create your models here.
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="USD")
    image_url = models.URLField(blank=True, null=True, max_length=500)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="inventory")
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product} qty={self.quantity}"
