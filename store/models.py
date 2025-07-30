from django.db import models
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count
# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=169, unique=True)
    slug = models.SlugField(max_length=169, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
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
# fetching reviews and displaying them as an average
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating')) # will give you the average of this field
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countReviews(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count += reviews['count']
        return count




# Now this class will help us to sort out our dropdown menus of color and size, by variation.variation_set.colors/sizes
# The name of the functions after variation_set
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (('color', 'color'),
                            ('size', 'size'))


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # if the product is delete we'll need to delete the review too
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=670, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=21, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now = True)

    def __str__(self): # string representation of the model
        return self.subject


# image gallery
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products/', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'Product_Gallery'
        verbose_name_plural = "Product Gallery"