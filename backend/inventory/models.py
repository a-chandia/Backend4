from django.db import models
from django.core.validators import MinValueValidator


# Bloque: Stock por sucursal.
# Relaciona Branch + Product y mantiene stock disponible.
class Inventory(models.Model):
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )

    # stock siempre >= 0 (el signal evita negativos, pero dejamos validador)
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    # punto de reposición (opcional, siempre >= 0)
    reorder_point = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('branch', 'product')
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"

    def __str__(self):
        return f"{self.product.name} - {self.branch.name} ({self.stock})"


# Bloque: Movimientos de inventario.
# Cada entrada o salida genera un registro histórico.
class InventoryMovement(models.Model):
    MOVEMENT_TYPES = [
    ('purchase', 'Purchase'),
    ('sale', 'Sale'),
    ('adjustment', 'Adjustment'),
    ('order', 'Order'),
]

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='movements'
    )

    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)

    # integer porque puede ser +n o -n
    quantity = models.IntegerField()

    reason = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements'
    )

    def __str__(self):
        sign = "+" if self.quantity > 0 else ""
        return f"{self.movement_type}: {sign}{self.quantity} ({self.inventory.product.name})"
