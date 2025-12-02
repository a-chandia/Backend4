from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone
# ---------------------------------------------------------
# Modelo Company
# Representa a la pyme cliente del sistema (MiniMarket,
# ferretería, etc.). Es la entidad base sobre la cual se
# agrupan usuarios, sucursales, productos y transacciones.
# ---------------------------------------------------------
PLAN_BRANCH_LIMITS = {
    'basic': 1,
    'standard': 3,
    'premium': None,  # None = ilimitado
}

class Company(models.Model):
    # -----------------------------------------------------
    # Nombre comercial de la empresa.
    # -----------------------------------------------------
    name = models.CharField(max_length=255)

    # -----------------------------------------------------
    # RUT de la empresa (único). Más adelante se puede
    # agregar un validador específico de RUT chileno.
    # -----------------------------------------------------
    rut = models.CharField(max_length=12, unique=True)

    # -----------------------------------------------------
    # Dirección principal de la empresa.
    # -----------------------------------------------------
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # -----------------------------------------------------
    # Teléfono de contacto de la empresa.
    # -----------------------------------------------------
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # -----------------------------------------------------
    # Fecha y hora en que la empresa fue creada en el sistema.
    # Se asigna automáticamente al crear el registro.
    # -----------------------------------------------------
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # -----------------------------------------------------
    # Indica si la empresa está activa en el sistema.
    # Sirve para “deshabilitar” una empresa sin eliminarla.
    # -----------------------------------------------------
    is_active = models.BooleanField(
        default=True
    )

    # -----------------------------------------------------
    # Representación en texto de la empresa, útil en el admin
    # y en listados.
    # -----------------------------------------------------
    def get_active_subscription(self):
        today = date.today()
        return self.subscriptions.filter(
            active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).order_by('-start_date').first()
    def get_active_subscription(self):
        from datetime import date
        today = date.today()
        return self.subscriptions.filter(
            active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).order_by('-start_date').first()

    def get_branch_limit(self):
        sub = self.get_active_subscription()
        if not sub:
            # sin suscripción => el sistema podría bloquear casi todo
            return 0
        return PLAN_BRANCH_LIMITS.get(sub.plan_name, 0)
    
    def __str__(self):
        return self.name
    

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Básico'),
        ('standard', 'Estándar'),
        ('premium', 'Premium'),
    ]

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan_name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validación pedida en la pauta: end_date > start_date
        if self.end_date <= self.start_date:
            raise ValidationError("La fecha de término debe ser mayor a la fecha de inicio.")

    def __str__(self):
        return f"{self.company.name} - {self.get_plan_name_display()}"

    class Meta:
        ordering = ['-start_date']    
