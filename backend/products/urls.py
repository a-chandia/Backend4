from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView

# Bloque: Router de productos.
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
