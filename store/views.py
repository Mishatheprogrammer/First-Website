from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from orders.models import OrderProduct
from django.contrib.auth.decorators import login_required
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.db.models import Q

def store(request, category_slug=None):
    categories = None
    items = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug) 
                                       # slug of this model
        items = Product.objects.all().filter(category=categories, is_available=True)
        # that way the category of the product is equal to the slug which corresponds with Category model
        paginator = Paginator(items, 3)
        page = request.GET.get('page')
        paged_items = paginator.get_page(page)
        item_count = items.count()
    else:
        items = Product.objects.all().filter(is_available=True)
        paginator = Paginator(items, 3)
        page = request.GET.get('page')# our url path, you'll understand once implemented at template
        paged_items = paginator.get_page(page)
        item_count = items.count()


    context = {
        'items': paged_items,
        'item_count': item_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # category__slug gets the slug of the category
        # double underscore is used to access the field of a related model
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()# True/False
        # in our 'carts' app we can see Cart.cart_id field of a model which is a foreign key of CartItem.cart
        # all of that code does is gets the unique session_id of the cart object in a shopping bin
        # _cart_id(request) is the function that we created in views.py at 'carts' app

    except Exception as e:
        raise e

    # Anonymous User error
    if request.user.is_authenticated:
    # Our review section
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
            # we are checking if the user has ordered this product before we are not taking it from anywhere
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None

    # get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status = True)

    # get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'order_product': order_product,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET: 
        keyword = request.GET['keyword']
# Here we are checking if GET request has this keyword or not, then we are storing the value as a keyword variable
        if keyword: # if it has something
            products = Product.objects.order_by('-created_at').filter(Q(product_name__icontains=keyword) | Q(description__icontains=keyword))
            # if the product_name has something similar to keyword than the product should pop up
            paginator = Paginator(products, 3)
            page = request.GET.get('page')# our url path, you'll understand once implemented at template
            paged_products = paginator.get_page(page)
            product_count = products.count()

    context = {
        'items': products,
        'item_count': product_count
    }
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER') # we are telling to store the previous url
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)# you are referring to the user's field import from another model which has its id
            form = ReviewForm(request.POST, instance=reviews)
            # we are passing this instance if you already have a review then you replace it,
            # if there's no review then you create it,
            # but if it exists the form will understand if we'll want to update the record
            form.save()
            messages.success(request, 'Thank you for you review! We updated your review! Opinions matter, one thinks...')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            # we create it if no record of the review is found for the user
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                # setting fields equal to the names of the forms with type="submit"
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR') # remote address stores ip address
                data.product_id = product_id # the one we passed in
                data.user_id = request.user.id
                data.save()
                messages.success(request, "ThankX! Your review has been submitted!")
                return redirect(url)
            
            else:
                messages.error(request, 'Your form went through our check and was found invalid!')
                return redirect(url)



    