from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, ReviewRating



def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_at')

# get the stars to show up dynamically
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)

def contact_us(request):
    return render(request, 'contact_us.html')

def about(request):
    return render(request, 'about.html')