from django.contrib.auth.models import AbstractUser
from django.db import models
from companies.models import Company
from branches.models import Branch
from core.validators import validate_rut   # ← importa aquí

ROLE_CHOICES = (
    ('super_admin', 'Super Administrador'),
    ('admin_cliente', 'Administrador Cliente'),
    ('gerente', 'Gerente'),
    ('vendedor', 'Vendedor'),
)

class User(AbstractUser):
    rut = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[validate_rut],
        help_text='RUT chileno, ej: 12345678-9'
    )

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='vendedor')
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    default_branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text='Sucursal principal del usuario (para vendedores POS).'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
