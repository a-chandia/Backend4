from rest_framework import serializers
from .models import User

# Bloque: Serializador base para el modelo User.
# Expone los campos principales del usuario y se usa para
# listar, obtener detalle y actualizar usuarios.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'rut',
            'role',
            'company',
            'is_active',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


# Bloque: Serializador para crear usuarios.
# Incluye el manejo del password de forma segura usando
# create_user para que se almacene encriptado.
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'rut',
            'role',
            'company',
            'password',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
