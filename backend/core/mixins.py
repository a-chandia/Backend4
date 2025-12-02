from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

# Bloque: mixin para restringir vistas por rol de usuario.
class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = None  # lista de roles permitidos

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if self.allowed_roles is not None and request.user.role not in self.allowed_roles:
            raise PermissionDenied("No tienes permiso para acceder a esta sección.")

        return super().dispatch(request, *args, **kwargs)
