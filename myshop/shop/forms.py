from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=64, label="login")
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=12)
    password = forms.CharField(max_length=16, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=16, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def clean(self):
        clean_data = super().clean()
        pas1 = clean_data['password']
        pas2 = clean_data['password2']
        if pas1 != pas2:
            raise ValidationError('Hasła się nie zgadzają')