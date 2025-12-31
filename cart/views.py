from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Min
from catalog.models import Product
from .models import Cart, CartItem


def _get_or_create_cart(user):
    with transaction.atomic():
        qs = Cart.objects.select_for_update().filter(user=user).order_by("id")
        if qs.exists():
            cart = qs.first()
            # Optional cleanup: delete extra carts
            extras = qs[1:]
            for c in extras:
                CartItem.objects.filter(cart=c).update(cart=cart)
                c.delete()
            return cart
        return Cart.objects.create(user=user)


def _cart_json(cart: Cart):
    items = []
    qs = CartItem.objects.select_related("product").filter(cart=cart).order_by("id")
    for it in qs:
        p = it.product
        items.append(
            {
                "id": it.id,
                "quantity": it.quantity,
                "product": {
                    "id": p.id,
                    "name": p.name,
                    "price_cents": p.price_cents,
                    "currency": p.currency,
                    "image_url": getattr(p, "image_url", None),
                },
            }
        )
    return {"id": cart.id, "items": items}


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def cart_detail(request):
    cart = _get_or_create_cart(request.user)

    if request.method == "DELETE":
        CartItem.objects.filter(cart=cart).delete()
        return Response({"detail": "Cart cleared."})

    return Response(_cart_json(cart))


@api_view(["POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def cart_items(request):
    cart = _get_or_create_cart(request.user)

    if request.method == "POST":
        product_id = request.data.get("product_id")
        qty = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"detail": "product_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if qty < 1:
            return Response({"detail": "quantity must be >= 1."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": qty})
        if not created:
            item.quantity += qty
            item.save(update_fields=["quantity"])

        return Response(_cart_json(cart), status=status.HTTP_201_CREATED)

    if request.method == "PATCH":
        item_id = request.data.get("item_id")
        qty = request.data.get("quantity")

        if not item_id:
            return Response({"detail": "item_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if qty is None:
            return Response({"detail": "quantity is required."}, status=status.HTTP_400_BAD_REQUEST)

        qty = int(qty)
        if qty < 1:
            return Response({"detail": "quantity must be >= 1."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        item.quantity = qty
        item.save(update_fields=["quantity"])
        return Response(_cart_json(cart))

    # DELETE
    item_id = request.data.get("item_id")
    if not item_id:
        return Response({"detail": "item_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        item = CartItem.objects.get(id=item_id, cart=cart)
    except CartItem.DoesNotExist:
        return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    item.delete()
    return Response(_cart_json(cart))
