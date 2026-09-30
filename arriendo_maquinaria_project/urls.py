"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
MÓDULO: RUTAS PRINCIPALES DEL PROYECTO (urls.py)
Autor: Gabriel Michibel | Sección: IEC-N4-C1 | Año: 2026
================================================================================
Define el enrutamiento general del sistema:
- Panel Administrativo de Django (/admin/)
- Endpoints REST y Documentación Swagger (/api/)
- Vistas del Frontend Web (/ , /catalogo/ , /carro/ , /mis-contratos/ , /panel/)
================================================================================
"""

from django.contrib import admin
from django.urls import path, include
from api import views as web_views

urlpatterns = [
    # Panel de administración Django
    path('admin/', admin.site.urls),

    # Rutas API REST y Swagger (Requisito /api/docs/)
    path('api/', include('api.urls')),

    # --------------------------------------------------------------------------
    # VISTAS FRONTEND (HTML5 / Bootstrap 5 / ES6)
    # --------------------------------------------------------------------------
    path('', web_views.catalogo_view, name='home'),
    path('catalogo/', web_views.catalogo_view, name='catalogo'),
    path('carro/', web_views.carro_view, name='carro'),
    path('mis-contratos/', web_views.mis_contratos_view, name='mis_contratos_web'),
    path('panel/', web_views.panel_ejecutivo_view, name='panel_ejecutivo_web'),
    path('login/', web_views.login_view, name='login_web'),
    path('auth/login/', web_views.login_view, name='login'),
]
