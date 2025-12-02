from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, TemplateView
from django.db import transaction
from django.utils import timezone

from rest_framework import viewsets, permissions

from core.mixins import RoleRequiredMixin
from products.models import Product
from inventory.models import Inventory
from branches.models import Branch
from companies.models import Company

from .models import Sale, SaleItem
from .serializers import SaleSerializer
from django.db.models import Sum
from .forms import SaleCreateForm , SaleItemSimpleForm 


# --------------------------------------------------------------------
# API REST: CRUD de ventas
# --------------------------------------------------------------------
class SaleViewSet(viewsets.ModelViewSet):
    """
    API de ventas. Filtra por company del usuario.
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if getattr(user, 'role', None) == 'super_admin':
            return Sale.objects.all().select_related('company', 'branch')

        if getattr(user, 'company', None):
            return Sale.objects.filter(company=user.company).select_related(
                'company', 'branch'
            )

        return Sale.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None)
        branch = getattr(user, 'default_branch', None)
        serializer.save(company=company, branch=branch, user=user)


# --------------------------------------------------------------------
# Vistas HTML clásicas (lista, creación, caja)
# --------------------------------------------------------------------
class SaleListView(RoleRequiredMixin, ListView):
    """
    Listado de ventas para admin_cliente / gerente / vendedor.
    """
    model = Sale
    template_name = 'sales_list.html'
    context_object_name = 'sales'
    allowed_roles = ['admin_cliente', 'gerente', 'vendedor', 'super_admin']

    def get_queryset(self):
        user = self.request.user

        if getattr(user, 'role', None) == 'super_admin':
            return Sale.objects.all().select_related('company', 'branch', 'created_by').order_by('-created_at')

        if not getattr(user, 'company', None):
            return Sale.objects.none()

        qs = Sale.objects.filter(company=user.company).select_related(
            'branch', 'created_by'
        )

        if user.role == 'vendedor' and user.default_branch:
            qs = qs.filter(branch=user.default_branch)

        return qs.order_by('-created_at')


class SaleCreateView(RoleRequiredMixin, View):
    allowed_roles = ['admin_cliente', 'gerente']
    template_name = 'sale_form.html'

    def get(self, request):
        user = request.user
        company = user.company
        branch = user.default_branch or Branch.objects.filter(company=company).first()

        sale_form = SaleCreateForm(initial={'branch': branch})
        item_form = SaleItemSimpleForm()
        products = Product.objects.filter(company=company, is_active=True)

        return render(request, self.template_name, {
            'sale_form': sale_form,
            'item_form': item_form,
            'products': products,
        })

    def post(self, request):
        user = request.user
        company = user.company

        sale_form = SaleCreateForm(request.POST)
        item_form = SaleItemSimpleForm(request.POST)
        products = Product.objects.filter(company=company, is_active=True)

        if not (sale_form.is_valid() and item_form.is_valid()):
            return render(request, self.template_name, {
                'sale_form': sale_form,
                'item_form': item_form,
                'products': products,
            })

        branch = sale_form.cleaned_data['branch']
        payment_method = sale_form.cleaned_data['payment_method']
        product = item_form.cleaned_data['product']
        quantity = item_form.cleaned_data['quantity']
        unit_price = product.price
        subtotal = unit_price * quantity

        try:
            with transaction.atomic():
                sale = Sale.objects.create(
                    company=company,
                    branch=branch,
                    user=user,
                    payment_method=payment_method,
                    total=Decimal('0'),
                )

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=unit_price,
                    subtotal=subtotal,
                )

                sale.total = subtotal
                sale.save()

        except ValueError as e:
            sale_form.add_error(None, str(e))
            return render(request, self.template_name, {
                'sale_form': sale_form,
                'item_form': item_form,
                'products': products,
            })

        return redirect('sales_list')


class CashReportView(RoleRequiredMixin, TemplateView):
    """
    Reporte simple de caja del día (ventas del día por sucursal del usuario).
    """
    template_name = 'cash_report.html'
    allowed_roles = ['admin_cliente', 'gerente', 'vendedor', 'super_admin']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        today = timezone.now().date()

        if user.role == 'super_admin':
            sales = Sale.objects.filter(date=today)
        elif getattr(user, 'company', None):
            qs = Sale.objects.filter(company=user.company, date=today)
            if user.role == 'vendedor' and user.default_branch:
                qs = qs.filter(branch=user.default_branch)
            sales = qs
        else:
            sales = Sale.objects.none()

        total_cash = sales.filter(payment_method='cash').aggregate(
            total=Sum('total')
        )['total'] or 0
        total_card = sales.filter(payment_method='card').aggregate(
            total=Sum('total')
        )['total'] or 0
        total_all = sales.aggregate(total=Sum('total'))['total'] or 0

        ctx['sales'] = sales
        ctx['total_cash'] = total_cash
        ctx['total_card'] = total_card
        ctx['total_all'] = total_all
        ctx['today'] = today
        return ctx


# --------------------------------------------------------------------
# POS con carrito (para vendedor) usando sesión
# --------------------------------------------------------------------

def _get_pos_cart(session):
    """
    Estructura del carrito POS en sesión:
    {
        "product_id": {
            "name": "...",
            "price": "1000.00",
            "quantity": 2
        },
        ...
    }
    """
    return session.get('pos_cart', {})


def _save_pos_cart(session, cart):
    session['pos_cart'] = cart
    session.modified = True


class POSView(RoleRequiredMixin, View):
    """
    Pantalla POS con carrito para vendedor (y opcionalmente gerente/admin_cliente).
    """
    allowed_roles = ['vendedor', 'gerente', 'admin_cliente']
    template_name = 'pos.html'

    def get(self, request):
        user = request.user
        branch = user.default_branch

        # Cargar inventario de esa sucursal
        inventories = Inventory.objects.filter(
            branch=branch,
            stock__gt=0
        ).select_related('product')

        products = []
        for inv in inventories:
            products.append({
                'product': inv.product,
                'stock': inv.stock,
            })

        # Cargar carrito POS
        cart = _get_pos_cart(request.session)
        cart_items = []
        cart_total = Decimal('0')

        for pid, data in cart.items():
            price = Decimal(data['price'])
            qty = data['quantity']
            subtotal = qty * price
            cart_total += subtotal

            cart_items.append({
                'product_id': pid,
                'name': data['name'],
                'price': price,
                'quantity': qty,
                'subtotal': subtotal,
            })

        return render(request, self.template_name, {
            'branch': branch,
            'products': products,
            'cart_items': cart_items,
            'cart_total': cart_total,
        })


class POSAddItemView(RoleRequiredMixin, View):
    """
    Agregar producto al carrito POS.
    """
    allowed_roles = ['vendedor', 'gerente', 'admin_cliente']

    def post(self, request, product_id):
        user = request.user
        branch = user.default_branch

        product = get_object_or_404(Product, id=product_id, is_active=True)
        inv = get_object_or_404(Inventory, branch=branch, product=product)

        qty = int(request.POST.get('quantity', 1))
        if qty <= 0:
            return redirect('pos')

        if inv.stock < qty:
            # Se podría agregar un mensaje de error en el contexto usando mensajes
            return redirect('pos')

        cart = _get_pos_cart(request.session)
        pid = str(product.id)

        if pid in cart:
            # Validar que no se supere el stock
            if cart[pid]['quantity'] + qty > inv.stock:
                return redirect('pos')
            cart[pid]['quantity'] += qty
        else:
            cart[pid] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': qty,
            }

        _save_pos_cart(request.session, cart)
        return redirect('pos')


class POSRemoveItemView(RoleRequiredMixin, View):
    """
    Quitar un producto del carrito POS.
    """
    allowed_roles = ['vendedor', 'gerente', 'admin_cliente']

    def post(self, request, product_id):
        cart = _get_pos_cart(request.session)
        pid = str(product_id)

        if pid in cart:
            del cart[pid]

        _save_pos_cart(request.session, cart)
        return redirect('pos')


class POSConfirmSaleView(RoleRequiredMixin, View):
    """
    Confirmar la venta desde el carrito POS.
    Crea un Sale + SaleItems. El descuento de stock se hace vía signals.
    """
    allowed_roles = ['vendedor', 'gerente', 'admin_cliente']

    def post(self, request):
        user = request.user
        branch = user.default_branch
        company = branch.company

        cart = _get_pos_cart(request.session)
        if not cart:
            return redirect('pos')

        try:
            with transaction.atomic():
                sale = Sale.objects.create(
                    company=company,
                    branch=branch,
                    user=user,
                    payment_method='efectivo',  # por defecto POS en efectivo
                    total=0,
                )

                total = Decimal('0')

                for pid, data in cart.items():
                    product = Product.objects.get(id=pid)
                    price = Decimal(data['price'])
                    qty = data['quantity']
                    subtotal = qty * price
                    total += subtotal

                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=qty,
                        price=price,      # <- usa 'price', no 'unit_price'
                        subtotal=subtotal,
                    )

                sale.total = total
                sale.save()

        except ValueError:
            return redirect('pos')

        _save_pos_cart(request.session, {})

        return redirect('sales_list')