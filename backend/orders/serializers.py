from rest_framework import serializers
from .models import Order, OrderItem

# Bloque: serializador ítems de pedido.
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id']


# Bloque: serializador de pedido con detalle.
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'company',
            'branch',
            'user',
            'customer_name',
            'customer_email',
            'status',
            'total',
            'created_at',
            'items',
        ]
        read_only_fields = ['id', 'created_at', 'user', 'total']

    # Bloque: create con cálculo de total.
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        user = request.user if request else None

        order = Order.objects.create(
            user=user,
            **validated_data
        )

        total = 0
        for item_data in items_data:
            quantity = item_data['quantity']
            price = item_data['price']
            subtotal = quantity * price

            OrderItem.objects.create(
                order=order,
                subtotal=subtotal,
                **item_data
            )

            total += subtotal

        order.total = total
        order.save()
        return order
