from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from django.views import View
from django.shortcuts import render, redirect
from core.mixins import RoleRequiredMixin
from .forms import AdminClienteCreateForm
from .models import User
from .forms import TenantUserCreateForm

# Bloque: ViewSet para el modelo User.
# Proporciona operaciones CRUD sobre usuarios.
# Usa un serializador para lectura/actualización y otro
# específico para creación (manejo de password).
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    # Bloque: Selección dinámica de serializador según acción.
    # create -> UserCreateSerializer (incluye password)
    # resto de acciones -> UserSerializer
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

class SuperAdminCreateAdminClienteView(RoleRequiredMixin, View):
    allowed_roles = ['super_admin']
    template_name = 'superadmin_admincliente_create.html'

    def get(self, request):
        form = AdminClienteCreateForm()
        admins = User.objects.filter(role='admin_cliente').select_related('company')
        return render(request, self.template_name, {
            'form': form,
            'admins': admins,
        })

    def post(self, request):
        form = AdminClienteCreateForm(request.POST)
        admins = User.objects.filter(role='admin_cliente').select_related('company')

        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
                'admins': admins,
            })

        form.save()
        return redirect('superadmin_admincliente_create')
    
class TenantUserListView(RoleRequiredMixin, View):
    """
    Lista usuarios de la misma empresa (gerentes / vendedores / admin_cliente).
    Solo visible para admin_cliente.
    """
    allowed_roles = ['admin_cliente']
    template_name = 'tenant_user_list.html'

    def get(self, request):
        company = request.user.company
        users = User.objects.filter(company=company).select_related('default_branch')
        return render(request, self.template_name, {
            'users': users,
        })


class TenantUserCreateView(RoleRequiredMixin, View):
    """
    Crea usuarios internos (gerente / vendedor) dentro de la empresa del admin_cliente.
    """
    allowed_roles = ['admin_cliente']
    template_name = 'tenant_user_form.html'

    def get(self, request):
        form = TenantUserCreateForm(company=request.user.company)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        company = request.user.company
        form = TenantUserCreateForm(request.POST, company=company)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        form.save(company=company)
        return redirect('tenant_user_list')    