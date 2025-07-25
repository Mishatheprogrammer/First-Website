from django.db import models
from store.models import Product, Variation
from accounts.models import Account
# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    
    variations = models.ManyToManyField(Variation, blank=True)

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    # models.CASCADE is going to delete the cart item if the cart is deleted
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity
        # this will return the subtotal of the product in the cart

    def __unicode__(self):
        return self.product