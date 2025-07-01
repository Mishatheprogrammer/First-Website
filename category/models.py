from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=False) 
    # The upload_to will upload the files of the objects to the photos which will be automatically created for us,
    # blank=false, means that that field must be filled in our admin panel
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def get_url(self):
        return reverse('product_by_category', args=[self.slug])
    # reversed is used to reverse the URL pattern,
    # 'products_by_category' is the name of the URL pattern we have created in urls.py
    # args=[self.slug] is used to pass the slug of the category to the URL pattern

    def __str__(self):
        return self.category_name