from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.contrib.auth import get_user_model, login, logout, authenticate
from .forms import CartAddProductForm, LoginForm, CreateUserForm, OrderCreateForm
from shop.cart import Cart
from shop.models import Category, Product, OrderItem, Order
from django.views import View


class ProductListView(View):
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


class ProductDetailView(View):
    def get(self, request, id, slug):
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        cart_product_form = CartAddProductForm()
        return render(request, 'shop/product/detail.html', {'product': product, 'cart_product_form': cart_product_form})

    def post(self, request, id, slug):
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        cart_product_form = CartAddProductForm(request.POST)
        return render(request, 'shop/product/detail.html', {'product': product, 'cart_product_form': cart_product_form})


class CartAddView(View):
    def post(self, request, product_id):
        form = CartAddProductForm(request.POST)
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update_quantity'])
        return redirect('cart-detail')
# @require_POST
# def cart_add(request, product_id):
#         form = CartAddProductForm(request.POST)
#         cart = Cart(request)
#         product = get_object_or_404(Product, id=product_id)
#         if form.is_valid():
#             cd = form.cleaned_data
#             cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
#         return redirect('cart-detail')


class CartRemoveView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('cart-detail')

# @require_POST
# def cart_remove(request, product_id):
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     cart.remove(product)
#     return redirect('cart-detail')


# def cartdetailview(request):
#     cart = Cart(request)
#     for item in cart:
#         item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'override': True})
#     return render(request, 'shop/cart/detail.html', {'cart': cart})


class CartDetailView(View):
    def get(self, request):
        cart = Cart(request)
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'override': True})
        return render(request, 'shop/cart/detail.html', {'cart': cart})


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
            else:
                return render(request, 'shop/user/login_user.html', {'form': form})
        else:
            return render(request, 'shop/user/login_user.html', {'form': form})


class CreateUserView(CreateView):
    form_class = CreateUserForm
    template_name = 'shop/user/add_user.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        user = form.save()
        user.is_active = True
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)


# class SignupView(View):
#     def get(self, request):
#         form = SignUpForm()
#         return render(request, 'exercises_app/add_user.html', {'form': form})
#
#     def post(self, request):
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('index')
#         return render(request, 'exercises_app/add_user.html', {'form': form})


class LogoutUserView(View):
    def get(self, request):
        logout(request)
        return redirect('product-list')


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
                return render(request, 'shop/order/created_order.html', {'order': order})
