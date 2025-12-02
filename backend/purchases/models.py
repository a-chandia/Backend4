from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from inventory.utils import register_inventory_movement
from core.validators import validate_rut
from companies.models import Company


# Bloque: Proveedor de la empresa.
# Asociado a una Company y usado en las compras.
class Supplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    rut = models.CharField(
        max_length=12,
        validators=[validate_rut],
        help_text='RUT chileno, ej: 12345678-9'
    )
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.rut})"


# Bloque: Cabecera de compra.
# Compra de productos para una sucursal a un proveedor.
class Purchase(models.Model):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchases'
    )
    date = models.DateField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases_created'
    )

    # Bloque: validación de la fecha de compra.
    # Evita registrar compras con fecha futura.
    def clean(self):
        super().clean()
        if self.date and self.date > now().date():
            raise ValidationError({'date': 'La fecha de la compra no puede ser futura.'})

    def __str__(self):
        return f"Compra #{self.id} - {self.supplier.name}"


# Bloque: Detalle de compra.
# Productos, cantidades y costos unitarios.
class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='purchase_items'
    )
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


# Bloque: signal para crear movimiento de inventario al crear PurchaseItem.
@receiver(post_save, sender=PurchaseItem)
def create_inventory_movement_for_purchase(sender, instance, created, **kwargs):
    if not created:
        return

    purchase = instance.purchase
    branch = purchase.branch
    product = instance.product
    quantity = instance.quantity
    user = purchase.created_by

    # Entrada de stock (compra) -> cantidad positiva.
    register_inventory_movement(
        branch=branch,
        product=product,
        quantity_change=quantity,
        movement_type='purchase',
        user=user,
        reason=f"Compra #{purchase.id}"
    )
