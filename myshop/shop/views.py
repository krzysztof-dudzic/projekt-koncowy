from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView
from django.contrib.auth import get_user_model, login, logout, authenticate, update_session_auth_hash
from .forms import CartAddProductForm, LoginForm, CreateUserForm, OrderCreateForm, SearchProductForm
from shop.cart import Cart
from shop.models import Category, Product, OrderItem, Order
from django.views import View
import random
from .tasks import order_created

"""
All views are used in this project.
"""

# home page
class HomePageView(View):
    def get(self, request):
        sorted_products = list(Product.objects.all())
        random.shuffle(sorted_products)
        three_products = sorted_products[:2]
        return render(request, 'shop/index.html',
                      context={'three_products': three_products})

# list of the products
class ProductListView(ListView):
    paginate_by = 2
    model = Product
    ordering = 'name'
    template_name = 'shop/product/list.html'

# detail of the product
class ProductDetailView(View):
    def get(self, request, id, slug):
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        cart_product_form = CartAddProductForm()
        return render(request, 'shop/product/detail.html', {'product': product, 'cart_product_form': cart_product_form})

    # def post(self, request, id, slug):
    #     product = get_object_or_404(Product, id=id, slug=slug, available=True)
    #     cart_product_form = CartAddProductForm(request.POST)
    #     return render(request, 'shop/product/detail.html', {'product': product, 'cart_product_form': cart_product_form})

# detail of the category
class CategoryDeatilView(View):
    def get(self, request, category_id):
        categories_id = Category.objects.get(id=category_id)
        products_category = Product.objects.filter(category=categories_id)
        return render(request, 'shop/category/category_products.html',
                      {'products_category': products_category, 'categories_id': categories_id})

# add to the cart
class CartAddView(View):
    def post(self, request, product_id):
        form = CartAddProductForm(request.POST)
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
        return redirect('cart-detail')

# remove product from the cart
class CartRemoveView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('cart-detail')

# detail of the cart
class CartDetailView(View):
    def get(self, request):
        cart = Cart(request)
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'override': True})
        return render(request, 'shop/cart/detail.html', context={'cart': cart})

# category view
class CategoryView(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'shop/category/category_view.html', context={'categories': categories})

# log in view
class LoginUserView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm
        return render(request, 'shop/user/login_user.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('product-list')
                # return HttpResponse("Jest ok")
            else:
                return render(request, 'shop/user/login_user.html', {'form': form})
        else:
            return render(request, 'shop/user/login_user.html', {'form': form})

# create uder/client
class CreateUserView(View):
    def get(self, request):
        form = CreateUserForm()
        return render(request, 'shop/user/add_user.html', {'form': form})

    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
        return render(request, 'shop/user/add_user.html', {'form': form})

# log out view
class LogoutUserView(View):
    def get(self, request):
        logout(request)
        return redirect('product-list')

# create order
class CreateOrderView(View):
    def get(self, request):
        cart = Cart(request)
        form = OrderCreateForm()
        return render(request, 'shop/order/create_order.html', {'cart': cart, 'form': form})

    def post(self, request):
        cart = Cart(request)
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear()
            order_created.delay(order.id)
            return render(request, 'shop/order/created_order.html', {'order': order})
        return render(request, 'shop/order/create_order.html', {'cart': cart, 'form': form})


# bought products
class HistoryOrderView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'shop/history_order/order.html'

# change password
class PasswordChangeView(LoginRequiredMixin, View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'shop/user/changepassword.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
        return redirect('password-change-done')

# after changed password
class PasswordChangeDoneView(View):
    def get(self, request):
        return render(request, 'shop/user/changepassword_done.html')


# search product
class SearchProductsView(View):
    def get(self, request):
        form = SearchProductForm()
        return render(request, 'shop/product/search_product.html', {'form': form})

    def post(self, request):
        form = SearchProductForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            list_of_products = Product.objects.filter(name__icontains=name)
            return render(request, 'shop/product/search_product.html',
                          {'form': form, 'list_of_products': list_of_products})
        return render(request, 'shop/product/search_product.html', {'form': form})
