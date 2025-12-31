from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_detail, name="cart-detail"),
    path("cart/items/", views.cart_items, name="cart-items"),
]
