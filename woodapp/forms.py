from django import forms
from .models import *


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        # fields = '__all__'
        fields = ['street', 'mobile']
        widgets = {
            'street': forms.TextInput(attrs={
                'class': 'username',
                'placeholder': 'Street'
            }),

            'mobile': forms.TextInput(attrs={
                'class': 'password',
                'placeholder': 'Mobile No'
            })
        }

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'username',
        'autocomplete': 'off',
        'placeholder': 'Enter Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'password',
        'autocomplete': 'new-password',
        'placeholder': 'Enter Password'

    }))


class SignupForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'username',
        'autocomplete': 'off',
        'placeholder': 'Enter Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'password',
        'autocomplete': 'new-password',
        'placeholder': 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'c_password',
        'placeholder': 'Confirm Password'
    }))
