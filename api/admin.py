"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
MÓDULO: ADMINISTRACIÓN DJANGO (admin.py)
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
================================================================================
Registra y personaliza los modelos en el panel de administración (/admin/):
- Usuario (con roles y atributos de constructora)
- Categoria (familias de equipos)
- Maquinaria (catálogo, tarifas y control de stock)
- CarroArriendo e ItemCarro (carro persistente)
- ContratoArriendo y DetalleContrato (gestión y snapshot histórico)
================================================================================
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario,
    Categoria,
    Maquinaria,
    CarroArriendo,
    ItemCarro,
    ContratoArriendo,
    DetalleContrato,
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Administración personalizada del modelo de Usuario con roles RBAC."""
    list_display = ('username', 'email', 'rol', 'razon_social', 'rut_empresa', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'razon_social', 'rut_empresa')
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Empresa y Rol RBAC', {
            'fields': ('rol', 'rut_empresa', 'razon_social', 'telefono'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Empresa y Rol RBAC', {
            'fields': ('rol', 'rut_empresa', 'razon_social', 'telefono'),
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Administración de Categorías."""
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    """Administración del inventario de Maquinarias."""
    list_display = ('id', 'nombre', 'categoria', 'tarifa_diaria', 'garantia_fija', 'unidades_disponibles', 'tiene_stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('unidades_disponibles', 'tarifa_diaria', 'garantia_fija')


class ItemCarroInline(admin.TabularInline):
    """Línea de ítems dentro de la vista de Carro."""
    model = ItemCarro
    extra = 0
    readonly_fields = ('dias_uso', 'costo_calculado')


@admin.register(CarroArriendo)
class CarroArriendoAdmin(admin.ModelAdmin):
    """Administración de Carros Persistentes."""
    list_display = ('id', 'usuario', 'total_items', 'fecha_actualizacion')
    search_fields = ('usuario__username', 'usuario__email')
    inlines = [ItemCarroInline]


class DetalleContratoInline(admin.TabularInline):
    """Línea de ítems históricos congelados dentro de Contrato."""
    model = DetalleContrato
    extra = 0
    readonly_fields = (
        'nombre_maquinaria', 'tarifa_diaria', 'garantia_fija',
        'fecha_inicio', 'fecha_fin', 'dias_uso', 'subtotal'
    )


@admin.register(ContratoArriendo)
class ContratoArriendoAdmin(admin.ModelAdmin):
    """Administración de Contratos de Arriendo y órdenes."""
    list_display = ('id', 'usuario', 'estado', 'monto_total', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('id', 'usuario__username', 'usuario__razon_social')
    list_editable = ('estado',)
    inlines = [DetalleContratoInline]
