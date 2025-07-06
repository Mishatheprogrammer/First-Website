from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password, please',
        'class':'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm, please',
        'class':'form-control',
    }))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    # Giving all our fields CSS properties, will loop through all the fields we have and give them bootstrap properties
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Ur First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Ur Last Name'
        self.fields['email'].widget.attrs['placeholder']=' Ur Email Address'
        self.fields['phone_number'].widget.attrs['placeholder']=' Ur Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
    # function to check password matches confirm_password
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('🤣Password Does Not Match!')