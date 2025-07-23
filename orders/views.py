from django.shortcuts import render, redirect
# from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from decimal import Decimal
import datetime
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import json
from django.http import JsonResponse


def payments(request):
    body = json.loads(request.body) # from our javascript in payments.html
    order = Order.objects.get(user=request.user, is_ordered=False, order_number = body['orderID'])
    # store transaction details inside Payment  model
    payment = Payment(user=request.user, 
                    payment_id = body['transID'], 
                    payment_method = body['payment_method'],
                    amount_paid = order.order_total, 
                    status = body['status']
                    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Here we'll move cart items below |
    #                                <-
    cart_items = CartItem.objects.filter(user=request.user)

    for cart_item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment # object we created for the class Payment()
        order_product.user_id = request.user.id
        order_product.product_id = cart_item.product_id
        order_product.qantity = cart_item.quantity
        order_product.product_price = cart_item.product.price
        order_product.ordered = True
        order_product.save()

        # saving the variations
        cart_itemss = CartItem.objects.get(id=cart_item.id)
        product_variation = cart_itemss.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

    # Reduce the quantity of the sold products in its stocks
        product = Product.objects.get(id=cart_item.product_id)
        product.stock -= cart_item.quantity
        product.save()
    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()
    # Send order received email to the customer
    mail_subject = 'ThanX for you paying us and you getting stuff from us. Order Received!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_mail = EmailMessage(mail_subject, message, to=[to_email])
    send_mail.send()

    # Send order number and transaction id back to the <script> in payments.html </script> sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)
# the above line of code will return the data to the payments.html where the json file is in <script>

def place_order(request):
    current_user = request.user # because we know that we are logged in now
    # if cart count is less than or equal to 0 then we'll redirect to the store page
    cart_items= CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = Decimal('0.00')
    tax = Decimal('0.00')
    total = Decimal('0.00')
    quantity = Decimal('0.00')
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = Decimal('0.02') * total
    grand_total = total + tax

    if request.method == "POST":
        # make sure to set form action={% url 'place_order' %}
        form = OrderForm(request.POST) # we need to create class OrderForm in a new forms.py file
        if form.is_valid():
            # Store all the billing information inside the table of class Order
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']# this is how you need to take values from forms
            data.address_line_1 = form.cleaned_data['address_line_1']# this is how you need to take values from forms
            data.phone_number = form.cleaned_data['phone_number']# this is how you need to take values from forms
            data.email = form.cleaned_data['email']# this is how you need to take values from forms
            data.city = form.cleaned_data['city']# this is how you need to take values from forms
            data.state = form.cleaned_data['state']# this is how you need to take values from forms, from its names
            data.country = form.cleaned_data['country']# this is how you need to take values from forms
            data.order_note = form.cleaned_data['order_note']# this is how you need to take values from forms
            data.address_line_2 = form.cleaned_data['address_line_2']

            data.order_total = grand_total
            data.tax = tax
    # data.status is already set as default 'New'
            data.ip = request.META.get('REMOTE_ADDR') # will you give you user's IP
            data.save()
            # Generating order ID
            year = int(datetime.date.today().strftime('%Y'))
            day = int(datetime.date.today().strftime('%d'))
            month = int(datetime.date.today().strftime('%m'))
            date = datetime.date(year, month, day)
            current_date = date.strftime('%Y%m%d') # 20250709
            order_number = current_date + str(data.id) # will always be unique
            data.order_number = order_number
            data.save()
# we will make it True once ordered
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist): # if the user puts in the wrong id
        return redirect('home')
