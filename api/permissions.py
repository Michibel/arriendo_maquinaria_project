"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
MÓDULO: PERMISOS DE ACCESO RBAC (permissions.py)
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
================================================================================
Implementa las políticas de autorización basadas en roles (RBAC) requeridas:
1. EsEjecutivoDeArriendos: Permite operaciones administrativas (gestión de catálogo,
   cambio de estado de contratos, consulta global de contratos).
2. EsEmpresaConstructora: Permite operaciones de cliente (gestionar su propio carro,
   realizar checkout y consultar 'mis contratos').
3. EsEjecutivoOReadOnly: Permite lectura pública a cualquier usuario, pero
   restringe escritura (POST/PUT/DELETE) exclusivamente a Ejecutivos.
================================================================================
"""

from rest_framework import permissions


class EsEjecutivoDeArriendos(permissions.BasePermission):
    """
    Permiso que valida si el usuario autenticado tiene el rol
    'EJECUTIVO_ARRIENDOS' o es Administrador (is_staff / is_superuser).
    """
    message = "Acceso restringido: Se requiere rol de Ejecutivo de Arriendos."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(request.user.es_ejecutivo)


class EsEmpresaConstructora(permissions.BasePermission):
    """
    Permiso que valida si el usuario autenticado tiene el rol
    'EMPRESA_CONSTRUCTORA' o es cliente en el sistema.
    """
    message = "Acceso restringido: Se requiere rol de Empresa Constructora."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Un ejecutivo o staff también puede realizar pruebas de cliente si es necesario
        return bool(request.user.es_constructora or request.user.es_ejecutivo)


class EsEjecutivoOReadOnly(permissions.BasePermission):
    """
    Permite métodos seguros (GET, HEAD, OPTIONS) a cualquier usuario (Público),
    pero exige rol de Ejecutivo de Arriendos para métodos de modificación
    (POST, PUT, PATCH, DELETE).
    """
    message = "Solo un Ejecutivo de Arriendos puede modificar el catálogo de maquinarias."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.es_ejecutivo
        )
