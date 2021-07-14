"""myshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from shop.views import ProductListView, ProductDetailView, CartRemoveView, CartAddView, CartDetailView, CategoryDeatilView
from shop.views import LoginUserView, LogoutUserView, CreateUserView, CreateOrderView, HomePageView, CategoryView
from shop.views import HistoryOrderView, PasswordChangeView, PasswordChangeDoneView, SearchProductsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('category/', CategoryView.as_view(), name='category-list'),
    path('<int:id>/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('category/<int:category_id>/', CategoryDeatilView.as_view(), name='category-detail'),
    # path('', include('myshop.urls', namespace='shop')),
    path('cart_detail/', CartDetailView.as_view(), name='cart-detail'),
    path('add/<int:product_id>/', CartAddView.as_view(), name='cart-add'),
    path('remove/<int:product_id>/', CartRemoveView.as_view(), name='cart-remove'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('add_user/', CreateUserView.as_view(), name='create-user'),
    path('create_order/', CreateOrderView.as_view(), name='create-order'),
    path('history_order/', HistoryOrderView.as_view(), name='history-order'),
    path('password_change/', PasswordChangeView.as_view(), name='password-change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password-change-done'),
    path('search_products/', SearchProductsView.as_view(), name='search-products'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
