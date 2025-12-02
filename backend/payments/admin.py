from django.contrib import admin
from .models import Payment

# Bloque: Admin de pagos.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'amount', 'payment_method', 'status', 'sale', 'order', 'created_at')
    list_filter = ('company', 'status', 'payment_method')
    search_fields = ('transaction_id',)
