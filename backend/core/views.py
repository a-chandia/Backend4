from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from core.mixins import RoleRequiredMixin
from products.models import Product
from sales.models import Sale
from purchases.models import Purchase
from inventory.models import Inventory
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.views import View
from django.shortcuts import render, redirect
from purchases.forms import PurchaseCreateForm, PurchaseItemSimpleForm
from purchases.models import Purchase, PurchaseItem
from sales.forms import SaleCreateForm, SaleItemSimpleForm
from sales.models import Sale, SaleItem
from purchases.models import Supplier
from purchases.forms import SupplierForm
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.utils.timezone import localdate
from django.db.models import Sum, Count
from django.shortcuts import redirect
from purchases.models import Supplier
from purchases.forms import SupplierForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from companies.models import Company, Subscription





from products.forms import ProductForm


# Bloque: dashboard general.
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    # Redirección por rol antes de cargar el template
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Vendedor: ir directo al POS / nueva venta
        if getattr(user, 'role', None) == 'vendedor':
            return redirect('pos')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == 'super_admin':
            ctx['companies_count'] = Company.objects.count()
            ctx['active_subscriptions_count'] = Subscription.objects.filter(active=True).count()
            ctx['products_count'] = 0
            ctx['sales_count'] = 0
            ctx['purchases_count'] = 0
            ctx['inventory_count'] = 0

        elif getattr(user, 'company', None):
            company = user.company
            ctx['products_count'] = Product.objects.filter(company=company).count()
            ctx['sales_count'] = Sale.objects.filter(company=company).count()
            ctx['purchases_count'] = Purchase.objects.filter(company=company).count()
            ctx['inventory_count'] = Inventory.objects.filter(branch__company=company).count()
            ctx['companies_count'] = 0
            ctx['active_subscriptions_count'] = 0

        else:
            ctx['products_count'] = 0
            ctx['sales_count'] = 0
            ctx['purchases_count'] = 0
            ctx['inventory_count'] = 0
            ctx['companies_count'] = 0
            ctx['active_subscriptions_count'] = 0

        return ctx


# Bloque: listado de productos.
class ProductListView(RoleRequiredMixin, ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente', 'vendedor']

    def get_queryset(self):
        qs = super().get_queryset()
        # Ejemplo: filtrar solo productos de la company del usuario (cuando lo tengas configurado)
        if self.request.user.is_authenticated and self.request.user.company:
            qs = qs.filter(company=self.request.user.company)
        return qs

# Bloque: listado de ventas.
class SaleListView(RoleRequiredMixin, ListView):
    model = Sale
    template_name = 'sales_list.html'
    context_object_name = 'sales'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente', 'vendedor']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not getattr(user, 'company', None):
            return qs.none()

        qs = qs.filter(company=user.company)

        if user.role == 'vendedor':
            # Vendedor: solo sus ventas (y normalmente su sucursal)
            if user.default_branch:
                qs = qs.filter(branch=user.default_branch, user=user)
            else:
                qs = qs.filter(user=user)

        # Gerente y admin_cliente ven todas las ventas de la empresa
        return qs

# Bloque: listado de compras.
class PurchaseListView(RoleRequiredMixin, ListView):
    model = Purchase
    template_name = 'purchases_list.html'
    context_object_name = 'purchases'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not getattr(user, 'company', None):
            return qs.none()

        # Todas las compras de la empresa (todas las sucursales)
        qs = qs.filter(company=user.company)
        return qs
  
    
# Bloque: listado de inventario.
class InventoryListView(RoleRequiredMixin, ListView):
    model = Inventory
    template_name = 'inventory_list.html'
    context_object_name = 'inventory_items'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente', 'vendedor']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not getattr(user, 'company', None):
            return qs.none()

        # Siempre filtrar por empresa
        qs = qs.filter(branch__company=user.company)

        # Vendedor: solo su sucursal
        if user.role == 'vendedor' and user.default_branch:
            qs = qs.filter(branch=user.default_branch)

        # admin_cliente y gerente: todas las sucursales de su empresa (ya filtrado arriba)
        return qs
    
    

# Bloque: logout simple.
# Cierra la sesión y redirige SIEMPRE al login.
def logout_view(request):
    logout(request)
    return redirect('login')

# Bloque: creación de productos (formulario HTML).
class ProductCreateView(RoleRequiredMixin, CreateView):
    model = Product
    template_name = 'product_form.html'
    fields = ['company', 'sku', 'name', 'description', 'price', 'cost', 'category', 'is_active']
    success_url = reverse_lazy('product_list')
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_initial(self):
        initial = super().get_initial()
        # Si el usuario tiene company asociada, la sugerimos por defecto
        if self.request.user.is_authenticated and self.request.user.company:
            initial['company'] = self.request.user.company
        return initial


# Bloque: edición de productos (formulario HTML).
class ProductUpdateView(RoleRequiredMixin, UpdateView):
    model = Product
    template_name = 'product_form.html'
    fields = ['company', 'sku', 'name', 'description', 'price', 'cost', 'category', 'is_active']
    success_url = reverse_lazy('product_list')
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtramos para que solo pueda editar productos de su propia empresa
        if self.request.user.is_authenticated and self.request.user.company:
            qs = qs.filter(company=self.request.user.company)
        return qs

class ProductCreateView(RoleRequiredMixin, CreateView):
    model = Product
    template_name = 'product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('product_list')
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated and getattr(self.request.user, 'company', None):
            initial['company'] = self.request.user.company
        return initial


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    model = Product
    template_name = 'product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('product_list')
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and getattr(self.request.user, 'company', None):
            qs = qs.filter(company=self.request.user.company)
        return qs
    

# Bloque: creación de compra + un ítem simple (HTML).
class PurchaseCreateView(RoleRequiredMixin, View):
    template_name = 'purchase_form.html'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get(self, request):
        purchase_form = PurchaseCreateForm(user=request.user)
        item_form = PurchaseItemSimpleForm(user=request.user)
        return render(request, self.template_name, {
            'purchase_form': purchase_form,
            'item_form': item_form,
        })

    def post(self, request):
        purchase_form = PurchaseCreateForm(request.POST, user=request.user)
        item_form = PurchaseItemSimpleForm(request.POST, user=request.user)

        if purchase_form.is_valid() and item_form.is_valid():
            if not getattr(request.user, 'company', None):
                purchase_form.add_error(None, "El usuario no tiene empresa asociada.")
                return render(request, self.template_name, {
                    'purchase_form': purchase_form,
                    'item_form': item_form,
                })

            # Crear cabecera de compra
            purchase = purchase_form.save(commit=False)
            purchase.company = request.user.company
            purchase.created_by = request.user
            purchase.total = 0  # se actualiza abajo
            purchase.save()

            # Crear ítem
            product = item_form.cleaned_data['product']
            quantity = item_form.cleaned_data['quantity']
            unit_cost = item_form.cleaned_data['unit_cost']
            subtotal = quantity * unit_cost

            PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                quantity=quantity,
                unit_cost=unit_cost,
                subtotal=subtotal,
            )

            # Actualizar total de la compra
            purchase.total = subtotal
            purchase.save()

            # El movimiento de inventario lo hace el signal de PurchaseItem
            return redirect('purchases_list')

        return render(request, self.template_name, {
            'purchase_form': purchase_form,
            'item_form': item_form,
        })


# Bloque: creación de venta (POS simple) + un ítem.
class SaleCreateView(RoleRequiredMixin, View):
    template_name = 'sale_form.html'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente', 'vendedor']
    http_method_names = ['get', 'post']  # explícitamente permitimos GET y POST

    def get(self, request):
        # reglas de rol / sucursal
        if request.user.role == 'vendedor' and not request.user.default_branch:
            raise PermissionDenied("El vendedor no tiene sucursal asignada.")

        sale_form = SaleCreateForm(user=request.user)
        item_form = SaleItemSimpleForm(user=request.user)

        products = Product.objects.filter(company=request.user.company) if getattr(request.user, 'company', None) else Product.objects.none()

        return render(request, self.template_name, {
            'sale_form': sale_form,
            'item_form': item_form,
            'products': products,
        })

    def post(self, request):
        sale_form = SaleCreateForm(request.POST, user=request.user)
        item_form = SaleItemSimpleForm(request.POST, user=request.user)

        if not getattr(request.user, 'company', None):
            sale_form.add_error(None, "El usuario no tiene empresa asociada.")
        if request.user.role == 'vendedor' and not request.user.default_branch:
            sale_form.add_error(None, "El vendedor no tiene sucursal asignada.")

        if not sale_form.is_valid() or not item_form.is_valid():
            products = Product.objects.filter(company=request.user.company) if getattr(request.user, 'company', None) else Product.objects.none()
            return render(request, self.template_name, {
                'sale_form': sale_form,
                'item_form': item_form,
                'products': products,
            })

        # Cabecera de venta
        sale = sale_form.save(commit=False)
        sale.company = request.user.company
        sale.user = request.user

        if request.user.role == 'vendedor':
            sale.branch = request.user.default_branch

        sale.total = 0
        sale.save()

        # Ítem
        product = item_form.cleaned_data['product']
        quantity = item_form.cleaned_data['quantity']
        price = product.price
        subtotal = quantity * price

        try:
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=price,
                subtotal=subtotal,
            )
        except ValueError as e:
            # error de stock insuficiente desde el signal de inventario
            sale.delete()
            msg = str(e) or "Stock insuficiente para realizar la operación."
            sale_form.add_error(None, msg)
            item_form.add_error(None, msg)
            products = Product.objects.filter(company=request.user.company) if getattr(request.user, 'company', None) else Product.objects.none()
            return render(request, self.template_name, {
                'sale_form': sale_form,
                'item_form': item_form,
                'products': products,
            })

        sale.total = subtotal
        sale.save()

        return redirect('sales_list')


from django.views.generic import ListView, CreateView, UpdateView
# ya las vienes usando

# Bloque: listado de proveedores.
class SupplierListView(RoleRequiredMixin, ListView):
    model = Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and getattr(self.request.user, 'company', None):
            qs = qs.filter(company=self.request.user.company)
        return qs


# Bloque: creación de proveedor.
class SupplierCreateView(RoleRequiredMixin, CreateView):
    model = Supplier
    template_name = 'supplier_form.html'
    form_class = SupplierForm
    success_url = reverse_lazy('supplier_list')
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ahora el form lo recibe y lo ignora sin romperse
        return kwargs

    def form_valid(self, form):
        if not getattr(self.request.user, 'company', None):
            form.add_error(None, "El usuario no tiene empresa asociada.")
            return self.form_invalid(form)

        supplier = form.save(commit=False)
        supplier.company = self.request.user.company  # aquí se asigna la empresa
        supplier.save()
        return redirect(self.success_url)



# Bloque: edición de proveedor.
class SupplierUpdateView(RoleRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'supplier_form.html'
    form_class = SupplierForm
    success_url = reverse_lazy('supplier_list')
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated and getattr(self.request.user, 'company', None):
            qs = qs.filter(company=self.request.user.company)
        return qs

# Bloque: resumen de caja del día (por sucursal / vendedor).
class CashReportView(RoleRequiredMixin, TemplateView):
    template_name = 'cash_report.html'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente', 'vendedor']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = localdate()

        qs = Sale.objects.filter(
            company=user.company,
            created_at__date=today
        )

        # Vendedor: solo su sucursal y sus ventas
        if user.role == 'vendedor':
            if user.default_branch:
                qs = qs.filter(branch=user.default_branch, user=user)
            else:
                qs = qs.none()
        # Gerente / admin_cliente / super_admin: TODAS las sucursales de la empresa (sin filtro extra)

        summary_by_method = qs.values('payment_method').annotate(
            total_amount=Sum('total'),
            count=Count('id'),
        ).order_by('payment_method')

        grand_total = qs.aggregate(total=Sum('total'))['total'] or 0

        context['today'] = today
        context['sales'] = qs
        context['summary_by_method'] = summary_by_method
        context['grand_total'] = grand_total
        return context

