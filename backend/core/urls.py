from django.urls import path
from .views import (
    DashboardView,
    ProductListView,
    SaleListView,
    PurchaseListView,
    InventoryListView,
    ProductCreateView,
    ProductUpdateView,
    PurchaseCreateView,
    SaleCreateView, 
    SupplierListView,
    SupplierCreateView,
    SupplierUpdateView,
    CashReportView,)
from sales.views import (POSView, POSAddItemView, POSRemoveItemView, POSConfirmSaleView )

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('products/new/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('sales/', SaleListView.as_view(), name='sales_list'),
    path('purchases/', PurchaseListView.as_view(), name='purchases_list'),
    path('inventory/', InventoryListView.as_view(), name='inventory_list'),
    path('purchases/new/', PurchaseCreateView.as_view(), name='purchase_create'),
    path('sales/new/', SaleCreateView.as_view(), name='sale_create'),
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('cash/', CashReportView.as_view(), name='cash_report'),
    path('pos/', POSView.as_view(), name='pos'),
    path('pos/add/<int:product_id>/', POSAddItemView.as_view(), name='pos_add'),
    path('pos/remove/<int:product_id>/', POSRemoveItemView.as_view(), name='pos_remove'),
    path('pos/confirm/', POSConfirmSaleView.as_view(), name='pos_confirm'),




    
]
