from django.contrib import admin
from .models import Category
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',),} 
    # dictionary with the key slug and the value is a tuple with the field that we want to prepopulate
    list_display = ('category_name', 'slug')

admin.site.register(Category, CategoryAdmin)