from django.test import TestCase
import pytest


def test_status_code(client):
    response = client.get('/category/')
    assert response.status_code == 200


def test_status_home(client):
    response = client.get('')
    assert response.status_code == 200


def test_status_products(client):
    response = client.get('/products/')
    assert response.status_code == 302


