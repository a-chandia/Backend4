from django.db import models

# Bloque: Sucursal de una empresa (Company).
class Branch(models.Model):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='branches'
    )
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # NUEVO: sucursal usada para pedidos web/e-commerce
    is_online_default = models.BooleanField(
        default=False,
        help_text="Si está marcada, esta sucursal se usa para los pedidos de la tienda online."
    )

    def __str__(self):
        return f"{self.name} - {self.company.name}"