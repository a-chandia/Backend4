from django.contrib import admin
from .models import Sale, SaleItem

# Bloque: inline para ítems de venta en admin.
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

# Bloque: Admin de Venta.
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'branch', 'user', 'total', 'payment_method', 'created_at')
    list_filter = ('company', 'branch', 'payment_method')
    inlines = [SaleItemInline]
