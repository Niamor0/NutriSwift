"""
URL configuration for main project.

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from foodorder.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home, name='home'),

    # Authentication URLs
    path('signup/', user_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('admin-login/', admin_login, name='admin_login'),
    path('logout/', user_logout, name='logout'),
    path('admin-logout/', admin_logout, name='admin_logout'),
    path('user-profile/', user_profile, name='user_profile'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    
    # Admin Dashboard URLs
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin_orders', admin_orders, name='admin_orders'),
    path('admin_users', admin_users, name='admin_users'),
    path('add_product/<str:product_type>/', add_product, name='add_product'),
    path('update_product/<str:product_type>/<int:product_id>/', update_product, name='update_product'),
    path('delete_product/<str:product_type>/<int:product_id>/', delete_product, name='delete_product'),
    path('delivery_management', delivery_management, name='delivery_management'),
    path('order_management', order_management, name='order_management'),
    path('admin_order_detail/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('update_order_status/<int:order_id>/status/', update_order_status, name='update_order_status'),


    # Product URLs
    path('pizza/', PizzaView, name='pizza'),
    path('burger/', BurgerView, name='burger'),
    path('pasta/', PastaView, name='pasta'),
    path('dessert/', DessertView, name='dessert'),
    # path('<str:product_type>/<int:product_id>/', product_detail, name='product_detail'),
    path('all_products/', AllProductsView, name='all_products'),

    # Cart URLs
    path('cart/', cart_view, name='cart_view'),
    path('add-to-cart/<str:product_type>/<int:product_id>/',add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', update_cart, name='update_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/',order_confirmation, name='order_confirmation'),
    path('order_detail/<int:order_id>/', order_detail, name='order_detail'),
    path('<str:product_type>/<int:product_id>/', product_detail, name='product_detail'),
    path('order-history/', order_history, name='order_history'),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()