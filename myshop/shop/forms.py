from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Order

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64, label="login")
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class CreateUserForm(UserCreationForm):
    username = forms.CharField(max_length=12)
    password = forms.CharField(max_length=16, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=16, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'password2', 'email']

    def clean(self):
        clean_data = super().clean()
        pas1 = clean_data['password']
        pas2 = clean_data['password2']
        if pas1 != pas2:
            raise ValidationError('Passwords are incorrect')


class OrderCreateForm(forms.Form):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
