from rest_framework import serializers
from .models import Inventory, InventoryMovement

# Bloque: Serializador Inventory.
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = [
            'id',
            'branch',
            'product',
            'stock',
            'reorder_point',
            'last_updated',
        ]
        read_only_fields = ['id', 'last_updated']


# Bloque: Serializador InventoryMovement.
class InventoryMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = [
            'id',
            'inventory',
            'movement_type',
            'quantity',
            'reason',
            'created_at',
            'user',
        ]
        read_only_fields = ['id', 'created_at']
