from django import forms
from .models import Order

# this function gives you a replication of the cllas Order in our models
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'order_note'] 
        # 10 total fields