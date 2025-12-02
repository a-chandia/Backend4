from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.utils import register_inventory_movement
from inventory.models import Inventory
# Bloque: Orden de venta e-commerce (cabecera).
# Representa una compra hecha por un cliente final vía web.
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('shipped', 'Enviada'),
        ('cancelled', 'Cancelada'),
    )

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    # Opcional: sucursal desde donde se despacha
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    # Datos del cliente (simple, sin cuenta)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    shipping_address = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Quién registró la orden internamente (si aplica)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_created'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.status})"


# Bloque: ítem de la orden.
# Productos, cantidades y precios unitarios.
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

@receiver(post_save, sender=OrderItem)
def create_inventory_movement_for_order(sender, instance, created, **kwargs):
    if not created:
        return

    order = instance.order
    product = instance.product
    quantity = instance.quantity

    if not order.branch:
        raise ValueError("La orden no tiene sucursal asignada.")

    try:
        inventory = Inventory.objects.get(
            branch=order.branch,
            product=product
        )
    except Inventory.DoesNotExist:
        raise ValueError(f"No hay inventario para '{product.name}' en la sucursal.")

    if inventory.stock < quantity:
        raise ValueError(f"Stock insuficiente para '{product.name}' en la sucursal.")

    # salida de stock (venta online)
    register_inventory_movement(
        branch=order.branch,
        product=product,
        quantity_change=-quantity,
        movement_type='order',
        user=order.created_by,
        reason=f"Orden web #{order.id}"
    )