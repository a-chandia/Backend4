from django.db import transaction
from .models import Inventory, InventoryMovement

# Bloque: actualiza stock y registra movimiento.
# - quantity_change: >0 entra stock, <0 sale stock.
@transaction.atomic
def register_inventory_movement(branch, product, quantity_change, movement_type, user=None, reason=""):
    inventory, created = Inventory.objects.get_or_create(
        branch=branch,
        product=product,
        defaults={'stock': 0}
    )

    new_stock = inventory.stock + quantity_change
    if new_stock < 0:
        raise ValueError("Stock insuficiente para realizar la operación.")

    inventory.stock = new_stock
    inventory.save()

    movement = InventoryMovement.objects.create(
        inventory=inventory,
        movement_type=movement_type,
        quantity=quantity_change,
        reason=reason,
        user=user,
    )

    return inventory, movement
