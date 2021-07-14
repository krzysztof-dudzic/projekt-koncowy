from .cart import Cart

# sharing cart for all templates
def cart(request):
    return {'cart': Cart(request)}
