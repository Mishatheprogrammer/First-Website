from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from decimal import Decimal
from django.http import HttpResponse
from store.models import Variation
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    return cart
    # this will return cart id

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
# Checks if the HTTP request is a POST request (usually from a form submission).
        for item in request.POST:
# Loops through all keys in the POST data
            key = item
# Assigns the current key (field name) to the variable key.
            value = request.POST[key]
# Gets the value associated with that key (the user's input for that field).
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
    # Here we are getting cart_id
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # get the cart using the cart_id() function present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    # CHECK IF THE CART_ITEM EXISTS OR NOT
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists() # true or false
    # Here we are adding a cart_item

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)


        # Logic: existing variations - - - > database
        #  product variations  - - - - > form submission, POST method
        #  item_id - - - - > database
        ex_variation_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_variation_list.append(list(existing_variation))
            id.append(item.id)


        if product_variation in ex_variation_list:
            # Increase cart_item quantity
            index = ex_variation_list.index(product_variation)
            item_id = id[index]
            # so basically you are finding an item in the list and adding it to the quantity
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity = 1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)# will add the whole list
        # cart_item.quantity += 1
        # is equal to the existing cart item quatity + 1
            item.save()
    else:
        cart_item = CartItem.objects.create(product=product, 
                                            quantity = 1, 
                                            cart=cart)

        # this will return cart item objects


        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')



def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def delete_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id= _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')



# After these functions we have successfully created or added a product to our cart
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        grand_total = 0
        tax = 0
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = total * Decimal('0.02')  # Assuming a tax rate of 2%
        grand_total = total + tax
    except Cart.DoesNotExist:
        tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        cart_items = []
        total = Decimal('0.00')
        quantity = 0
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'grand_total': grand_total,
        'tax': tax,
    }

    return render(request, 'store/cart.html', context)