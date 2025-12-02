from rest_framework import serializers
from .models import Product

# Bloque: Serializador principal de productos.
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'company',
            'sku',
            'name',
            'description',
            'price',
            'cost',
            'category',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    # Bloque: validaciones básicas de negocio.
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value

    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("El costo no puede ser negativo.")
        return value
