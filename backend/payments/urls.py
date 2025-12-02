from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

# Bloque: router de pagos.
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
