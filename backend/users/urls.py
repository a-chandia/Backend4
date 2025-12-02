from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .views import SuperAdminCreateAdminClienteView
from .views import TenantUserListView, TenantUserCreateView
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('superadmin/users/new-admin-cliente/', SuperAdminCreateAdminClienteView.as_view(),
         name='superadmin_admincliente_create'),
    path('tenant/users/', TenantUserListView.as_view(), name='tenant_user_list'),
    path('tenant/users/new/', TenantUserCreateView.as_view(), name='tenant_user_create'),   
         
]
