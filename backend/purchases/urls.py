from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, PurchaseViewSet

# Bloque: Router de compras y proveedores.
router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchases', PurchaseViewSet, basename='purchase')

urlpatterns = [
    path('', include(router.urls)),
]
