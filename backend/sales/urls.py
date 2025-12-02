from django.urls import path
from .views import POSView, POSAddItemView, POSRemoveItemView, POSConfirmSaleView

urlpatterns = [
    path('pos/', POSView.as_view(), name='pos'),
    path('pos/add/<int:product_id>/', POSAddItemView.as_view(), name='pos_add'),
    path('pos/remove/<int:product_id>/', POSRemoveItemView.as_view(), name='pos_remove'),
    path('pos/confirm/', POSConfirmSaleView.as_view(), name='pos_confirm'),
]
