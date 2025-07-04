from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse

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
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
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

    