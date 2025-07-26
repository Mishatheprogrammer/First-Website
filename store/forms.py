from django import forms
from .models import ReviewRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating # model we want to use to fill in our form to
        fields = ['subject', 'review', 'rating']# fields from the model