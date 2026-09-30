"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
MÓDULO: RUTAS API REST (urls.py de la app 'api')
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
================================================================================
Define el enrutamiento para:
- JWT Authentication (Login con claims RBAC, Refresh, Registro y Perfil)
- CRUD de Catálogo de Maquinarias y Categorías (Routers DRF)
- Carro de Arriendo persistente en PostgreSQL (Consulta, Adición, Eliminación)
- Checkout Atómico y Consulta de Mis Contratos
- Documentación Swagger / OpenAPI interactiva en /api/docs/
================================================================================
"""

from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (
    CustomTokenObtainPairView,
    RegistroUsuarioView,
    PerfilUsuarioView,
    CategoriaViewSet,
    MaquinariaViewSet,
    CarroArriendoView,
    CarroItemEliminarView,
    CarroVaciarView,
    CheckoutContratoView,
    MisContratosListView,
    ContratoViewSet,
    DashboardStatsView,
)

app_name = 'api'

# Configuración del Router DRF para ViewSets
router = routers.DefaultRouter()
router.register(r'maquinarias', MaquinariaViewSet, basename='maquinaria')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'contratos', ContratoViewSet, basename='contrato')

urlpatterns = [
    # --------------------------------------------------------------------------
    # 1. AUTENTICACIÓN Y ROLES (SimpleJWT + Claims)
    # --------------------------------------------------------------------------
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('auth/register/', RegistroUsuarioView.as_view(), name='auth_register'),
    path('auth/me/', PerfilUsuarioView.as_view(), name='auth_me'),

    # --------------------------------------------------------------------------
    # 2. CARRO DE ARRIENDO PERSISTENTE (Empresa Constructora)
    # --------------------------------------------------------------------------
    path('carro-arriendo/', CarroArriendoView.as_view(), name='carro_arriendo'),
    path('carro-arriendo/<int:item_id>/', CarroItemEliminarView.as_view(), name='carro_item_eliminar'),
    path('carro-arriendo/vaciar/', CarroVaciarView.as_view(), name='carro_vaciar'),

    # --------------------------------------------------------------------------
    # 3. CHECKOUT ATÓMICO Y CONTRATOS DEL CLIENTE
    # --------------------------------------------------------------------------
    path('contratos/checkout/', CheckoutContratoView.as_view(), name='contratos_checkout'),
    path('mis-contratos/', MisContratosListView.as_view(), name='mis_contratos'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),

    # --------------------------------------------------------------------------
    # 4. RUTAS DEL ROUTER (Maquinarias, Categorías, Contratos Ejecutivos)
    # --------------------------------------------------------------------------
    path('', include(router.urls)),

    # --------------------------------------------------------------------------
    # 5. DOCUMENTACIÓN OPENAPI / SWAGGER (Requisito de la pauta)
    # Accesible en /api/docs/ y esquema en /api/schema/
    # --------------------------------------------------------------------------
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
]
