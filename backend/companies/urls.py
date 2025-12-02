# companies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet  # tu API
from .views import (
    SuperAdminCompanyListView,
    SuperAdminCompanyDetailView,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    # API REST
    path('', include(router.urls)),

    # VISTAS HTML para super_admin
    path('superadmin/companies/', SuperAdminCompanyListView.as_view(), name='superadmin_company_list'),
    path('superadmin/companies/<int:pk>/', SuperAdminCompanyDetailView.as_view(), name='superadmin_company_detail'),
]
