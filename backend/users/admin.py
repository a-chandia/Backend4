from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Bloque: configuración de User en el admin, con company y default_branch.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # columnas que se ven en la tabla de usuarios
    list_display = ('username', 'email', 'role', 'company', 'default_branch', 'is_staff', 'is_active')
    list_filter = ('role', 'company', 'is_staff', 'is_active')

    # campos mostrados en el formulario de edición
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rut', 'role', 'company', 'default_branch'),
        }),
    )

    # campos al crear un usuario nuevo
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('rut', 'role', 'company', 'default_branch'),
        }),
    )
