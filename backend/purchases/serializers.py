from rest_framework import serializers
from .models import Supplier, Purchase, PurchaseItem
from inventory.utils import register_inventory_movement

# Bloque: Serializador de proveedor.
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id',
            'company',
            'name',
            'rut',
            'contact_name',
            'contact_email',
            'contact_phone',
            'address',
        ]
        read_only_fields = ['id']


# Bloque: Serializador de ítems de compra.
class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = [
            'id',
            'product',
            'quantity',
            'unit_cost',
            'subtotal',
        ]
        read_only_fields = ['id']


# Bloque: Serializador de compra con detalle anidado.
class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = [
            'id',
            'company',
            'branch',
            'supplier',
            'date',
            'total',
            'created_at',
            'created_by',
            'items',
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'total']

        # Bloque: create con detalle y cálculo de total.
    # El inventario se actualiza vía signal de PurchaseItem.
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        user = request.user if request else None

        purchase = Purchase.objects.create(
            created_by=user,
            **validated_data
        )

        total = 0
        for item_data in items_data:
            quantity = item_data['quantity']
            unit_cost = item_data['unit_cost']
            subtotal = quantity * unit_cost

            PurchaseItem.objects.create(
                purchase=purchase,
                subtotal=subtotal,
                **item_data
            )
            total += subtotal

        purchase.total = total
        purchase.save()
        return purchase

