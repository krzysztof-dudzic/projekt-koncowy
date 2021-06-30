from django.shortcuts import render, get_object_or_404


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
        return render(request, 'myshop/product/list.html',
                      {'category': category,
                      'categories': categories,
                      'products': products})


class ProductDetail(View):
    def get(self, request, id, slug):
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        return render(request, 'myshop/product/list.html', {'product': product})


