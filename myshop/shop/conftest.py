import pytest
from django.test import Client
from shop.models import Product

# for the tests

@pytest.fixture
def product():
    products = Product.objects.all()
    return products


@pytest.fixture
def client():
    client = Client()
    return client