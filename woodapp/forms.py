from django import forms
from .models import *


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        # fields = '__all__'
        fields = ['street', 'mobile']
