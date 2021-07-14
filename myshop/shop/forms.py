from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Order

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]


'''
Forms using in the project
'''
# Add product to the cart
class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

# form for logging in
class LoginForm(forms.Form):
    username = forms.CharField(max_length=64, label="login")
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

# create user/client in the shop
class CreateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=12)
    password = forms.CharField(max_length=16,label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=16, label="Repeat password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'password2', 'email']

    def clean(self):
        clean_data = self.cleaned_data
        pas1 = clean_data['password']
        pas2 = clean_data['password2']
        if pas1 != pas2:
            raise ValidationError('Passwords are incorrect')

# create order
class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

# search product
class SearchProductForm(forms.Form):
    name = forms.CharField(label="Nazwa produktu", max_length=250)