from django.contrib import admin
from .models import Inventory, InventoryMovement

# Bloque: Admin Inventory.
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('branch', 'product', 'stock', 'reorder_point')
    list_filter = ('branch', 'product')
    search_fields = ('product__name',)


# Bloque: Admin InventoryMovement.
@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'movement_type', 'quantity', 'created_at', 'user')
    list_filter = ('movement_type',)
