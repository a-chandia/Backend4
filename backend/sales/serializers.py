from rest_framework import serializers
from .models import Sale, SaleItem
from inventory.utils import register_inventory_movement
# Bloque: Serializador de ítems de venta.
class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id']


# Bloque: Serializador de venta con ítems anidados.
class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'company',
            'branch',
            'user',
            'total',
            'payment_method',
            'created_at',
            'items'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'total']
        
    # Bloque: create con detalle y cálculo de total.
    # El inventario se actualiza vía signal de SaleItem.
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        user = request.user if request else None

        sale = Sale.objects.create(
            user=user,
            **validated_data
        )

        total = 0
        for item_data in items_data:
            quantity = item_data['quantity']
            price = item_data['price']
            subtotal = quantity * price

            SaleItem.objects.create(
                sale=sale,
                subtotal=subtotal,
                **item_data
            )
            total += subtotal

        sale.total = total
        sale.save()
        return sale

