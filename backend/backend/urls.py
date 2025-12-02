from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import logout_view  # <- importar nuestra función
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Interfaz HTML principal (dashboard y vistas core)
    path('', include('core.urls')),

    # Login (usa la plantilla registration/login.html)
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),

    # Logout propio: redirige al login
    path('logout/', logout_view, name='logout'),

    # Admin Django
    path('admin/', admin.site.urls),

    # API REST
    path('api/', include('companies.urls')),
    path('api/', include('users.urls')),
    path('api/', include('branches.urls')),
    path('api/', include('products.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('purchases.urls')),
    path('api/', include('sales.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('payments.urls')),
    #ENDPOINTS JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include('core.urls')),
    path('', include('orders.urls')),
]
