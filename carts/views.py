from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from decimal import Decimal
from django.http import HttpResponse
from store.models import Variation
from django.contrib.auth.decorators import login_required
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    return cart
    # this will return cart id

def add_cart(request, product_id):
# to handle logged in and out users' shopping bin
    current_user = request.user

    product = Product.objects.get(id=product_id)
# if the user is authenticated
    if current_user.is_authenticated:
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

            # CHECK IF THE CART_ITEM EXISTS OR NOT
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists() # true or false
            # Here we are adding a cart_item

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)# we don't need cart=cart because we are logged
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
                    # so basically you are finding an item in the list and adding it to the quantity if you find it
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                # cart_item.quantity += 1
                # is equal to the existing cart item quatity + 1
                item.save()
            else: # if you don't find it then create a new one
                item = CartItem.objects.create(product=product, quantity = 1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)# will add the whole list

                item.save()
        else:
            cart_item = CartItem.objects.create(product=product, 
                                                quantity = 1, 
                                                user=current_user)

                # this will return cart item objects


            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')


# If the user is not authenticated

    else: # the rest of the code
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists() # true or false
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_variation_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_variation_list:
                index = ex_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else: # if you don't find it then create a new one
                item = CartItem.objects.create(product=product, quantity = 1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)# will add the whole list
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
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
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
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
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
        # saving cart based off of user's status - > logged in/not logged in
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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

@login_required(login_url = 'login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = Decimal("0.00")
        grand_total = Decimal('0.00')
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True) # we don't need session id because we can access user's data instead
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = total * Decimal('0.02')
        grand_total = total + tax
    except Cart.DoesNotExist:
        tax = Decimal('0.00')
        grand_total = Decimal("0.00")
        cart_items = []
        total = Decimal("0.00")
        quantity = 0

    context = {
        'grand_total':grand_total,
        'tax':tax,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)