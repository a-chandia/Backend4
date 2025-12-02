from rest_framework import viewsets, permissions
from .models import Inventory, InventoryMovement
from .serializers import InventorySerializer, InventoryMovementSerializer

# Bloque: CRUD de inventario.
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]


# Bloque: CRUD de movimientos de inventario.
class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
