from django.contrib import admin
from .models import Product, Variation, ReviewRating
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'slug', 'price', 'stock', 'is_available')
    list_display_links = ('product_name', 'stock')
    prepopulated_fields = {'slug': ('product_name',)}
    # This will automatically fill the slug field based on the product name

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_display_links = ('product', 'variation_category')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')



admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)