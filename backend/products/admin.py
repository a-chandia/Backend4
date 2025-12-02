from django.contrib import admin
from .models import Product

# Bloque: Configuración admin para productos.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'company', 'price', 'is_active')
    list_filter = ('company', 'is_active', 'category')
    search_fields = ('name', 'sku')
