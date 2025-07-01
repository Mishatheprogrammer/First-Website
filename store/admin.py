from django.contrib import admin
from .models import Product
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'slug', 'price', 'stock', 'is_available')
    list_display_links = ('product_name', 'stock')
    prepopulated_fields = {'slug': ('product_name',)}
    # This will automatically fill the slug field based on the product name

admin.site.register(Product, ProductAdmin)