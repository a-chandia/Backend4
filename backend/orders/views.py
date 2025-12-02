from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer

from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django import forms

from products.models import Product
from orders.models import Order, OrderItem
from core.permissions import IsCompanyUser
from branches.models import Branch
from django.db import transaction
from django.views.generic import ListView, DetailView
from core.mixins import RoleRequiredMixin
from companies.models import Company
from branches.models import Branch
from inventory.models import Inventory
# Bloque: CRUD API de pedidos.
# Bloque: CRUD API de pedidos.
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, 'company', None):
            return Order.objects.none()
        # admin_cliente / gerente ven órdenes de su empresa
        qs = Order.objects.filter(company=user.company)
        # si quisieras limitar vendedor, aquí filtras:
        # if user.role == 'vendedor': qs = qs.filter(created_by=user)
        return qs

    # Pasar request al serializer (para user).
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        user = self.request.user
        company = user.company
        # branch opcional (puedes leerla del body si la envías por API)
        branch = None
        serializer.save(
            company=company,
            branch=branch,
            created_by=user,
        )

# Bloque: formulario de checkout (datos cliente).
class CheckoutForm(forms.Form):
    customer_name = forms.CharField(
        label='Nombre',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    customer_email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    customer_phone = forms.CharField(
        label='Teléfono',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_address = forms.CharField(
        label='Dirección de envío',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


# Utilidades de carrito (session)
def _get_cart(session):
    return session.get('cart', {})


def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


# Bloque: listado público de productos (catálogo simple).
class ShopProductListView(View):
    template_name = 'shop_product_list.html'

    def get(self, request):
        # Empresa demo: tomamos la primera (puedes ajustar esto si usas varias)
        company = Company.objects.first()

        # Determinar sucursal online
        branch = None
        if company:
            branch = Branch.objects.filter(company=company, is_online_default=True).first()
            if not branch:
                branch = Branch.objects.filter(company=company).first()

        # Lista de productos con stock para esa sucursal
        products_data = []

        if company and branch:
            inventories = (
                Inventory.objects
                .filter(branch=branch, product__is_active=True)
                .select_related('product')
            )

            for inv in inventories:
                products_data.append({
                    'product': inv.product,
                    'stock': inv.stock,
                })
        else:
            # Fallback: mostrar productos activos sin stock asociado
            for p in Product.objects.filter(is_active=True):
                products_data.append({
                    'product': p,
                    'stock': None,
                })

        # Cargar carrito desde sesión
        cart = _get_cart(request.session)
        cart_items = []
        cart_total = Decimal('0')

        for pid, data in cart.items():
            price = Decimal(data['price'])
            qty = data['quantity']
            subtotal = price * qty
            cart_total += subtotal
            cart_items.append({
                'product_id': pid,
                'name': data['name'],
                'price': price,
                'quantity': qty,
                'subtotal': subtotal,
            })

        return render(request, self.template_name, {
            'products_data': products_data,
            'cart_items': cart_items,
            'cart_total': cart_total,
            'branch': branch,
            'company': company,
        })




# Bloque: agregar producto al carrito.
class CartAddView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = _get_cart(request.session)

        pid = str(product.id)
        quantity = int(request.POST.get('quantity', 1))

        if pid in cart:
            cart[pid]['quantity'] += quantity
        else:
            cart[pid] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity,
            }

        _save_cart(request.session, cart)
        return redirect('shop_product_list')


# Bloque: ver carrito.
class CartDetailView(View):
    template_name = 'cart_detail.html'

    def get(self, request):
        cart = _get_cart(request.session)
        items = []
        total = Decimal('0')

        for pid, data in cart.items():
            price = Decimal(data['price'])
            qty = data['quantity']
            subtotal = price * qty
            total += subtotal
            items.append({
                'product_id': pid,
                'name': data['name'],
                'price': price,
                'quantity': qty,
                'subtotal': subtotal,
            })

        return render(request, self.template_name, {
            'items': items,
            'total': total,
        })


# Bloque: quitar un ítem del carrito.
class CartRemoveView(View):
    def post(self, request, product_id):
        cart = _get_cart(request.session)
        pid = str(product_id)
        if pid in cart:
            del cart[pid]
            _save_cart(request.session, cart)
        return redirect('shop_product_list')


# Bloque: checkout (datos cliente + creación de Order/OrderItem).
class CheckoutView(View):
    template_name = 'checkout.html'

    def get(self, request):
        cart = _get_cart(request.session)
        if not cart:
            return redirect('shop_product_list')

        form = CheckoutForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        cart = _get_cart(request.session)
        if not cart:
            return redirect('shop_product_list')

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            # El formulario tiene errores de validación
            return render(request, self.template_name, {'form': form})

       # Tomamos la company del primer producto del carrito
        first_pid = next(iter(cart.keys()))
        first_product = Product.objects.get(id=first_pid)
        company = first_product.company

# Buscamos la sucursal marcada como "online" para esa empresa
        branch = Branch.objects.filter(company=company, is_online_default=True).first()
        if not branch:
    # Si no hay ninguna marcada, usamos la primera sucursal como respaldo
            branch = Branch.objects.filter(company=company).first()

            if not branch:  
                form.add_error(None, "No hay ninguna sucursal configurada para la empresa.")
            return render(request, self.template_name, {'form': form})


        try:
            with transaction.atomic():
                order = Order.objects.create(
                    company=company,
                    branch=branch,
                    customer_name=form.cleaned_data['customer_name'],
                    customer_email=form.cleaned_data['customer_email'],
                    customer_phone=form.cleaned_data['customer_phone'],
                    shipping_address=form.cleaned_data['shipping_address'],
                    status='pending',
                    created_by=request.user if request.user.is_authenticated else None,
                    total=0,  # lo calculamos abajo
                )

                total = Decimal('0')
                for pid, data in cart.items():
                    product = Product.objects.get(id=pid)
                    price = Decimal(data['price'])
                    qty = data['quantity']
                    subtotal = price * qty
                    total += subtotal

                    # Aquí se dispara el signal que descuenta stock
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        unit_price=price,
                        subtotal=subtotal,
                    )

                order.total = total
                order.save()

        except ValueError as e:
            # Errores desde el signal de inventario (stock insuficiente, sin inventario, etc.)
            form.add_error(None, str(e) or "No fue posible completar la orden.")
            return render(request, self.template_name, {'form': form})

        # Vaciar carrito
        _save_cart(request.session, {})

        # Aquí es donde DEBE redirigir
        return redirect('order_success', order_id=order.id)

# Bloque: pantalla simple de confirmación.
class OrderSuccessView(View):
    template_name = 'order_success.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, self.template_name, {'order': order})
    
# Bloque: listado de órdenes e-commerce para panel interno.
class OrderListView(RoleRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_queryset(self):
        user = self.request.user

        if not getattr(user, 'company', None):
            return Order.objects.none()

        qs = Order.objects.filter(company=user.company).select_related('branch')

        # Si quisieras filtrar más por rol, lo haces aquí.
        # Por ejemplo: si gerente solo debería ver ciertas sucursales.

        return qs.order_by('-created_at')


# Bloque: detalle de una orden e-commerce.
class OrderDetailView(RoleRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'
    allowed_roles = ['super_admin', 'admin_cliente', 'gerente']

    def get_queryset(self):
        user = self.request.user

        if not getattr(user, 'company', None):
            return Order.objects.none()

        # Solo permitir ver órdenes de su empresa
        return Order.objects.filter(company=user.company).select_related('branch')    