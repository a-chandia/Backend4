from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from companies.models import Company
from branches.models import Branch
from users.models import User
from inventory.utils import register_inventory_movement


# Bloque: Cabecera de venta presencial en sucursal.
class Sale(models.Model):
    PAYMENT_METHODS = (
        ('efectivo', 'Efectivo'),
        ('credito', 'Tarjeta Crédito'),
        ('transferencia', 'Transferencia'),
        ('debito', 'Tarjeta Débito'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='efectivo'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.id} - {self.branch.name}"


# Bloque: Ítems de venta.
class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='sale_items'
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


# Bloque: signal para crear movimiento de inventario al crear SaleItem.
@receiver(post_save, sender=SaleItem)
def create_inventory_movement_for_sale(sender, instance, created, **kwargs):
    if not created:
        return

    sale = instance.sale
    branch = sale.branch
    product = instance.product
    quantity = instance.quantity
    user = sale.user

    # Salida de stock (venta) -> cantidad negativa.
    register_inventory_movement(
        branch=branch,
        product=product,
        quantity_change=-quantity,
        movement_type='sale',
        user=user,
        reason=f"Venta #{sale.id}"
    )
