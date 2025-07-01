from django.db import models
from django.urls import reverse
# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=169, unique=True)
    slug = models.SlugField(max_length=169, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    image = models.ImageField(upload_to='photos/products', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    #   ('category_model.Your_Category_Model_Name', on_delete=models.CASCADE - >
    # Whenever you delete the category, all the products in that category will be deleted as well😋
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
 


