from myshop.settings import BRAINTREE_CONF
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView
from django.contrib.auth import get_user_model, login, logout, authenticate, update_session_auth_hash
from .forms import CartAddProductForm, LoginForm, CreateUserForm, OrderCreateForm, SearchProductForm
from shop.cart import Cart
from shop.models import Category, Product, OrderItem, Order
from django.views import View
import random
from .tasks import order_created
import braintree
from django.template.loader import render_to_string
import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
"""
All views are used in this project.
"""


# home page
class HomePageView(View):
    def get(self, request):
        sorted_products = list(Product.objects.all())
        random.shuffle(sorted_products)
        three_products = sorted_products[:3]
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
            request.session['order_id'] = order.id
            return redirect('payment-process')
            # return render(request, 'shop/order/created_order.html', {'order': order})
        return render(request, 'shop/order/create_order.html', {'cart': cart, 'form': form})


# bought products
class HistoryOrderView(LoginRequiredMixin, View):
    def get(self, request):
        orders = OrderItem.objects.all()
        return render(request, 'shop/history_order/order.html', {'orders': orders})


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

gateway = braintree.BraintreeGateway(BRAINTREE_CONF)


class PaymentProcessView(View):
    def get(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        client_token = braintree.ClientToken.generate()
        return render(request, 'shop/payment/process.html', {'order': order, 'client_token': client_token})

    def post(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        nonce = request.POST.get('payment_method_nonce', None)
        result = braintree.Transaction.sale({
            'amount': '{:.2f}'.format(order.get_total_cost()),
            'payment_method_none': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            order.paid = True
            order.braintree_id = result.transaction.id
            order.save()
            return redirect('payment-done')
        else:
            return redirect('payment-canceled')


class PaymentDoneView(View):
    def get(self, request):
        return render(request, 'shop/payment/done.html')


class PaymentCanceledView(View):
    def get(self, request):
        return render(request, 'shop/payment/canceled.html')


# @staff_member_required
# def admin_order_detail(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     return render(request, 'shop/admin/detail.html', {'order': order})

class AdminOrder(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'shop/admin/detail.html', {'order': order})


class AdminOrderPdf(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        html = render_to_string('shop/order/pdf.html', {'order': order})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=\"order_{}.pdf"'.format(order.id)
        weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(
            settings.STATIC_ROOT + 'css/pdf.css')])

        return response
