from rest_framework import serializers
from .models import Branch

# Bloque: Serializador Branch.
# Expone los campos de la sucursal vía API.
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            'id',
            'company',
            'name',
            'address',
            'phone',
        ]
        read_only_fields = ['id']
