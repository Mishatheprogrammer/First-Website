from django.db import models
from accounts.models import Account
from store.models import Product, Variation
# Create your models here.
# <  - - - - > Fine, bro 8 h 14 min left
class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    amount_paid = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

# will collect all the data from the checkout submission form
class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
# order_object.payment can be linked to one Payment record. If that Payment objects is deleted, set 
# order_object.payment to Null instead of deleting it, for user to fill it up laternull=True allows to be null in db
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=100)
    # Data from the form - ->
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    # End of form submission < -  - - - -
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),        # ('db_value', 'human_readable_value')
        ('Completed', 'Completed'),      # first 'New' value gets stored in the database
        ('Cancelled', 'Cancelled'),      # second 'New' value is what will be displayed in admin interface
    )
    status = models.CharField(max_length=10, choices=STATUS, default='New')

    ip = models.CharField(max_length=200, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)
    def order_number_integer(self):
        return int(self.order_number)

    def full_address(self):
        return f'{self.address_line_1}; {self.address_line_2}'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.first_name

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)  # variation can be empty, so blank=True
    #color = models.CharField(max_length=69) don't need them, because we are getting all these things inside the variation
    #size = models.CharField(max_length=69)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.product.product_name