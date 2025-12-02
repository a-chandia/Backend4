from rest_framework import viewsets, permissions
from .models import Branch
from .serializers import BranchSerializer
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.contrib import messages
from core.mixins import RoleRequiredMixin

# Bloque: ViewSet Branch.
# CRUD completo para sucursales.
class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

class BranchCreateView(RoleRequiredMixin, CreateView):
    model = Branch
    template_name = 'branch_form.html'
    fields = ['name', 'address', 'phone']
    allowed_roles = ['admin_cliente']

    def form_valid(self, form):
        user = self.request.user
        company = user.company

        # Límite según plan
        branch_limit = company.get_branch_limit()
        current_count = Branch.objects.filter(company=company).count()

        if branch_limit is not None and current_count >= branch_limit:
            form.add_error(None, f"Plan alcanzado: solo puede tener {branch_limit} sucursal(es) con su plan actual.")
            return self.form_invalid(form)

        form.instance.company = company
        return super().form_valid(form)