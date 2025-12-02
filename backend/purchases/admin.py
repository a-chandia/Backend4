from django.contrib import admin
from .models import Supplier, Purchase, PurchaseItem

# Bloque: Admin Supplier.
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'rut', 'company', 'contact_email', 'contact_phone')
    list_filter = ('company',)
    search_fields = ('name', 'rut')


# Bloque: Inline para ítems de compra.
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


# Bloque: Admin Purchase.
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'branch', 'supplier', 'date', 'total')
    list_filter = ('company', 'branch', 'supplier')
    inlines = [PurchaseItemInline]
