from rest_framework import viewsets, permissions
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Product
from .serializers import ProductSerializer
from .forms import ProductForm
from core.permissions import IsCompanyUser, ProductPermission

# API
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsCompanyUser, ProductPermission]

    # Bloque: filtrar productos por company del usuario (multi-tenant).
    def get_queryset(self):
        user = self.request.user
        qs = Product.objects.none()
        if user.is_authenticated and getattr(user, 'company', None):
            qs = Product.objects.filter(company=user.company)
        return qs

    # Bloque: al crear un producto por API, forzar company = user.company.
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(company=user.company)

# Templates
class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")
