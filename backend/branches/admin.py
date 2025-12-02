from django.contrib import admin
from .models import Branch

# Bloque: Admin para Branch.
# Permite gestión básica desde Django Admin.
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'address')
    list_filter = ('company',)
    search_fields = ('name',)
