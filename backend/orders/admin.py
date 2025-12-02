from django.contrib import admin
from .models import Order, OrderItem

# Bloque: inline de ítems de pedido.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Bloque: admin de pedidos.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'branch', 'customer_name', 'status', 'total', 'created_at')
    list_filter = ('company', 'branch', 'status')
    search_fields = ('customer_name', 'customer_email')
    inlines = [OrderItemInline]
