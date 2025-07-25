from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product



def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)