from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
# Create your views here.
def store(request, category_slug=None):
    categories = None
    items = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug) 
                                       # slug of this model
        items = Product.objects.all().filter(category=categories, is_available=True)
        # that way the category of the product is equal to the slug which corresponds with Category model
        item_count = items.count()
    else:
        items = Product.objects.all().filter(is_available=True)
        item_count = items.count()


    context = {
        'items': items,
        'item_count': item_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # category__slug gets the slug of the category
        # double underscore is used to access the field of a related model
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
    }
    return render(request, 'store/product_detail.html', context)

    