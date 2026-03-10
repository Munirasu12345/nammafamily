from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('forgot_password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
]