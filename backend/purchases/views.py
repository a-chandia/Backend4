from rest_framework import viewsets, permissions
from .models import Supplier, Purchase
from .serializers import SupplierSerializer, PurchaseSerializer

# Bloque: CRUD API de proveedores.
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]


# Bloque: CRUD API de compras.
class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Bloque: inyectar request en el serializer (para created_by).
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
