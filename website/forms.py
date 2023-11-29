# forms.py

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Rating (out of 5)',
            'comment': 'Comment',
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
