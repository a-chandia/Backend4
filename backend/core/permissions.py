from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

class IsCompanyUser(BasePermission):
    """
    Solo usuarios autenticados con company asociada.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'company', None) is not None
        )

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'super_admin'
        )
    
class ProductPermission(BasePermission):
    """
    Permisos por rol para Product:
    - admin_cliente / gerente: pueden listar, crear, actualizar.
    - vendedor: solo lectura (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not getattr(user, 'company', None):
            return False

        # super_admin: acceso total
        if user.role == 'super_admin':
            return True

        # admin_cliente y gerente: lectura y escritura
        if user.role in ['admin_cliente', 'gerente']:
            return True

        # vendedor: solo lectura
        if user.role == 'vendedor':
            return request.method in SAFE_METHODS

        return False
