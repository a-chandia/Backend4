from rest_framework import serializers
from .models import Payment

# Bloque: Serializador de pagos.
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'company',
            'amount',
            'payment_method',
            'status',
            'transaction_id',
            'created_at',
            'sale',
            'order',
        ]
        read_only_fields = ['id', 'created_at']

    # Bloque: validación simple del monto.
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value
