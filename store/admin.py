from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image') # image fields
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    # but we want to display an image in the admin panel, that's why we use thumbnails
    # pip install django-admin-thumbnails

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'slug', 'price', 'stock', 'is_available')
    list_display_links = ('product_name', 'stock')
    prepopulated_fields = {'slug': ('product_name',)}
    # This will automatically fill the slug field based on the product name
    inlines = [ProductGalleryInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_display_links = ('product', 'variation_category')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')



admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)