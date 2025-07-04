from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return ()
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1]) # [row:position:step], so first one in list
# A queryset is a collection of database objects.
# Here, it’s used to get all items belonging to the current user’s cart (not all carts, just the one for this session).

            # we want to get cartitem_quantity
            for cart_item in cart_items:
                cart_count += cart_item.quantity # because you access the field of class cart
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)