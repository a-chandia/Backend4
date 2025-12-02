# companies/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Company, Subscription
from .serializers import CompanySerializer, SubscriptionSerializer
from core.permissions import IsSuperAdmin, IsCompanyUser
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import transaction

from core.mixins import RoleRequiredMixin
from .models import Company, Subscription
from .forms import CompanyForm, SubscriptionForm


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if getattr(user, 'role', None) == 'super_admin':
            return Company.objects.all()

        if getattr(user, 'company', None):
            return Company.objects.filter(id=user.company.id)

        return Company.objects.none()

    def get_permissions(self):
        # Solo super_admin puede crear companies
        if self.action in ['create', 'subscribe']:
            return [IsSuperAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # super_admin crea empresas clientes
        serializer.save()

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """
        POST /api/companies/{id}/subscribe/
        Body: { "plan_name": "basic|standard|premium", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }
        """
        company = self.get_object()

        data = request.data.copy()
        data['company'] = company.id

        # Opcional: marcar todas las suscripciones anteriores como inactivas
        Subscription.objects.filter(company=company, active=True).update(active=False)

        serializer = SubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()

        return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)

# Bloque: listado y creación rápida de empresas clientes.
class SuperAdminCompanyListView(RoleRequiredMixin, View):
    allowed_roles = ['super_admin']
    template_name = 'superadmin_company_list.html'

    def get(self, request):
        companies = Company.objects.all().order_by('name')
        form = CompanyForm()
        return render(request, self.template_name, {
            'companies': companies,
            'form': form,
        })

    def post(self, request):
        form = CompanyForm(request.POST)
        companies = Company.objects.all().order_by('name')

        if not form.is_valid():
            return render(request, self.template_name, {
                'companies': companies,
                'form': form,
            })

        form.save()
        return redirect('superadmin_company_list')


# Bloque: detalle de empresa + gestión de suscripciones.
class SuperAdminCompanyDetailView(RoleRequiredMixin, View):
    allowed_roles = ['super_admin']
    template_name = 'superadmin_company_detail.html'

    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        subscriptions = company.subscriptions.order_by('-start_date')
        form = SubscriptionForm()
        return render(request, self.template_name, {
            'company': company,
            'subscriptions': subscriptions,
            'form': form,
        })

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        subscriptions = company.subscriptions.order_by('-start_date')
        form = SubscriptionForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {
                'company': company,
                'subscriptions': subscriptions,
                'form': form,
            })

        with transaction.atomic():
            # Opcional: desactivar suscripción activa anterior
            Subscription.objects.filter(company=company, active=True).update(active=False)

            new_sub = form.save(commit=False)
            new_sub.company = company
            new_sub.save()

        return redirect('superadmin_company_detail', pk=company.pk)
