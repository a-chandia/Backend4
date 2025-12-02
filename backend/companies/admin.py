from django.contrib import admin
from .models import Company
from .models import Subscription 
# ---------------------------------------------------------
# Configuración del modelo Company en el panel de admin.
# Permite crear, editar y listar empresas desde el
# administrador de Django.
# ---------------------------------------------------------
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    # -----------------------------------------------------
    # Columnas que se muestran en la lista de empresas.
    # -----------------------------------------------------
    list_display = ('name', 'rut', 'is_active', 'created_at')

    # -----------------------------------------------------
    # Filtros laterales para acotar la búsqueda.
    # -----------------------------------------------------
    list_filter = ('is_active',)

    # -----------------------------------------------------
    # Campos por los que se puede buscar en el listado.
    # -----------------------------------------------------
    search_fields = ('name', 'rut')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan_name', 'start_date', 'end_date', 'active')
    list_filter = ('plan_name', 'active')
    search_fields = ('company__name',)