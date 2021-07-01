from django.shortcuts import render, get_object_or_404, redirect
from .forms import CartAddProductForm
from shop.cart import Cart
from shop.models import Category, Product
from django.views import View


class ProductList(View):
    def get(self, request, category_slug=None):
        category = None
        categories = Category.objects.all()
        products = Product.objects.filter(available=True)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        return render(request, 'shop/product/list.html',
                      {'category': category,
                      'categories': categories,
                      'products': products})


class ProductDetail(View):
    def get(self, request, id, slug):
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        return render(request, 'shop/product/detail.html', {'product': product})


class CartAddView(View):
    def get(self, request, product_id):
        form = CartAddProductForm()
        return render(request, 'shop/cart/detail.html', {'form': form})

    def post(self, request, product_id):
        form = CartAddProductForm(request.POST)
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
        return render(request, 'shop/cart/detail.html', {'form': form, 'cart': cart, 'product': product})


class CartRemoveView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('cart-add')
