from django.shortcuts import render

from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from cart.models import Cart
from catalog.models import Inventory
from .models import Order, OrderItem, OrderEvent
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items", "events")

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """
        Converts the authenticated user's cart into an order, decrements inventory.
        Payment can be added next (Stripe PaymentIntent).
        """
        try:
            cart = Cart.objects.prefetch_related("items__product__inventory").get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        if not cart.items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(user=request.user, status="pending", currency="USD", total_cents=0)
            total = 0

            for item in cart.items.select_related("product"):
                product = item.product
                inv = Inventory.objects.select_for_update().get(product=product)

                if inv.quantity < item.quantity:
                    raise ValueError(f"Insufficient inventory for {product.name}")

                inv.quantity -= item.quantity
                inv.save()

                total += product.price_cents * item.quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    unit_price_cents=product.price_cents,
                    quantity=item.quantity,
                )

            order.total_cents = total
            order.save()
            OrderEvent.objects.create(order=order, event="Order created from cart")
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
