from django.urls import path
from .views import (
    ShopProductListView,
    CartAddView,
    CartDetailView,
    CartRemoveView,
    CheckoutView,
    OrderSuccessView,
    OrderListView,
    OrderDetailView,
)

urlpatterns = [
    # Rutas públicas e-commerce
    path('shop/', ShopProductListView.as_view(), name='shop_product_list'),
    path('shop/cart/', CartDetailView.as_view(), name='cart_detail'),
    path('shop/cart/add/<int:product_id>/', CartAddView.as_view(), name='cart_add'),
    path('shop/cart/remove/<int:product_id>/', CartRemoveView.as_view(), name='cart_remove'),
    path('shop/checkout/', CheckoutView.as_view(), name='checkout'),
    path('shop/order/<int:order_id>/success/', OrderSuccessView.as_view(), name='order_success'),

    # Rutas internas (panel)
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]
