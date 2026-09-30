"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN (RENTING / SERVICIOS)
MÓDULO: MODELOS DE DATOS (models.py)
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
Base de Datos: PostgreSQL
================================================================================
Este archivo define la capa de persistencia e integridad relacional del sistema:
1. Usuario (AbstractUser con RBAC: Empresa Constructora vs Ejecutivo de Arriendos)
2. Categoria (Familias de maquinaria: Excavación, Elevación, etc.)
3. Maquinaria (Equipos disponibles con stock, tarifas y garantías)
4. CarroArriendo (Carro persistente 1 a 1 por usuario en PostgreSQL)
5. ItemCarro (Ítem con cálculo automático de días de uso y costo)
6. ContratoArriendo (Orden de arriendo con CHOICES de estado)
7. DetalleContrato (Snapshot histórico congelado de maquinaria y valores)
================================================================================
"""

from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone


# ==============================================================================
# BLOQUE 1: MODELO DE USUARIO PERSONALIZADO (RBAC)
# Roles soportados:
# - Empresa Constructora (Cliente)
# - Ejecutivo de Arriendos (Administrador / Gestor de Maquinarias y Contratos)
# ==============================================================================
class Usuario(AbstractUser):
    """
    Extensión del modelo de usuario nativo de Django para implementar
    Control de Acceso Basado en Roles (RBAC).
    """
    ROL_EMPRESA = 'EMPRESA_CONSTRUCTORA'
    ROL_EJECUTIVO = 'EJECUTIVO_ARRIENDOS'

    ROLES_CHOICES = [
        (ROL_EMPRESA, 'Empresa Constructora'),
        (ROL_EJECUTIVO, 'Ejecutivo de Arriendos'),
    ]

    rol = models.CharField(
        max_length=30,
        choices=ROLES_CHOICES,
        default=ROL_EMPRESA,
        verbose_name="Rol en el Sistema",
        help_text="Define los permisos del usuario (Cliente Constructora o Gestor Ejecutivo)"
    )
    rut_empresa = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="RUT Empresa / Persona",
        help_text="Ejemplo: 76.123.456-K"
    )
    razon_social = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Razón Social / Empresa",
        help_text="Nombre de la empresa constructora o institución"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono de Contacto"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios del Sistema"

    def __str__(self):
        nombre_display = self.razon_social or self.get_full_name() or self.username
        return f"{nombre_display} ({self.get_rol_display()})"

    @property
    def es_ejecutivo(self):
        """Verifica si el usuario tiene rol de Ejecutivo de Arriendos o es Superuser."""
        return self.rol == self.ROL_EJECUTIVO or self.is_staff or self.is_superuser

    @property
    def es_constructora(self):
        """Verifica si el usuario tiene rol de Empresa Constructora."""
        return self.rol == self.ROL_EMPRESA


# ==============================================================================
# BLOQUE 2: MODELO CATEGORIA
# Clasificación de maquinaria pesada y equipos de construcción.
# ==============================================================================
class Categoria(models.Model):
    """
    Representa una categoría o familia de maquinaria.
    Ejemplos: Movimiento de Tierras, Elevación y Carga, Generación Eléctrica.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Categoría"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción de la Categoría"
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías de Maquinaria"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==============================================================================
# BLOQUE 3: MODELO MAQUINARIA
# Catálogo de equipos pesados disponibles para arriendo.
# ==============================================================================
class Maquinaria(models.Model):
    """
    Modelo representativo de cada maquinaria disponible en flota.
    Registra tarifa diaria, garantía obligatoria, stock y multimedia.
    """
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='maquinarias',
        verbose_name="Categoría"
    )
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre de la Maquinaria"
    )
    descripcion = models.TextField(
        verbose_name="Descripción y Especificaciones Técnicas"
    )
    tarifa_diaria = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Tarifa Diaria (CLP/USD)"
    )
    garantia_fija = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Garantía Fija Obligatoria"
    )
    unidades_disponibles = models.PositiveIntegerField(
        default=1,
        verbose_name="Unidades Disponibles en Flota (Stock)"
    )
    imagen_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="URL de Imagen del Equipo"
    )

    class Meta:
        verbose_name = "Maquinaria"
        verbose_name_plural = "Maquinarias de Construcción"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (Stock: {self.unidades_disponibles})"

    @property
    def tiene_stock(self):
        """Indica si existen unidades disponibles para ser arrendadas."""
        return self.unidades_disponibles > 0


# ==============================================================================
# BLOQUE 4: MODELO CARRO ARRIENDO (1 a 1 con Usuario)
# Garantiza persistencia en PostgreSQL independiente de la sesión del cliente.
# ==============================================================================
class CarroArriendo(models.Model):
    """
    Carro de compras de arriendos asociado de manera persistente
    a cada usuario (Empresa Constructora) en base de datos PostgreSQL.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='carro',
        verbose_name="Usuario Propietario"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Modificación"
    )

    class Meta:
        verbose_name = "Carro de Arriendo"
        verbose_name_plural = "Carros de Arriendo"

    def __str__(self):
        return f"Carro de {self.usuario.username}"

    def calcular_total(self):
        """Calcula el costo total sumando todos los ítems actuales en el carro."""
        return sum(item.costo_calculado for item in self.items.all())

    def total_items(self):
        """Retorna la cantidad de equipos en el carro."""
        return self.items.count()


# ==============================================================================
# BLOQUE 5: MODELO ITEM CARRO
# Registro individual de un equipo en el carro con cálculo automático.
# Días de Uso = fecha_fin - fecha_inicio (mínimo 1 día)
# Costo Ítem = (tarifa_diaria * dias_uso) + garantia_fija
# ==============================================================================
class ItemCarro(models.Model):
    """
    Ítem individual contenido dentro del CarroArriendo.
    Calcula automáticamente los días y el costo total en base a las fechas.
    """
    carro = models.ForeignKey(
        CarroArriendo,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Carro Asociado"
    )
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.CASCADE,
        related_name='en_carros',
        verbose_name="Maquinaria Seleccionada"
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio del Arriendo"
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha de Término del Arriendo"
    )
    dias_uso = models.PositiveIntegerField(
        verbose_name="Días de Uso Estimados",
        editable=False
    )
    costo_calculado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Costo Calculado (Tarifa + Garantía)",
        editable=False
    )

    class Meta:
        verbose_name = "Ítem de Carro"
        verbose_name_plural = "Ítems de Carro"

    def clean(self):
        """Validación de consistencia de fechas antes de guardar."""
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError("La fecha de término no puede ser anterior a la fecha de inicio.")

    def save(self, *args, **kwargs):
        """
        Calcula automáticamente los días de uso y el costo total:
        Días de Uso = max(1, (fecha_fin - fecha_inicio).days)
        Costo Ítem = (tarifa_diaria * dias_uso) + garantia_fija
        """
        self.clean()
        delta = (self.fecha_fin - self.fecha_inicio).days
        self.dias_uso = max(1, delta)
        
        tarifa_total = self.maquinaria.tarifa_diaria * Decimal(self.dias_uso)
        self.costo_calculado = tarifa_total + self.maquinaria.garantia_fija
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.maquinaria.nombre} ({self.dias_uso} días: ${self.costo_calculado})"


# ==============================================================================
# BLOQUE 6: MODELO CONTRATO ARRIENDO (ORDEN)
# Estados oficiales definidos en la pauta de evaluación.
# ==============================================================================
class ContratoArriendo(models.Model):
    """
    Contrato u Orden formal de arriendo de maquinaria.
    Maneja el flujo de ciclo de vida del arriendo mediante CHOICES estrictos.
    """
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_PAGADO = 'PAGADO'
    ESTADO_ENTREGADO = 'ENTREGADO'
    ESTADO_COMPLETADO = 'COMPLETADO'
    ESTADO_CANCELADO = 'CANCELADO'

    ESTADOS_CHOICES = [
        (ESTADO_PENDIENTE, 'PENDIENTE'),
        (ESTADO_PAGADO, 'PAGADO'),
        (ESTADO_ENTREGADO, 'ENTREGADO'),
        (ESTADO_COMPLETADO, 'COMPLETADO'),
        (ESTADO_CANCELADO, 'CANCELADO'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contratos',
        verbose_name="Cliente Registrado"
    )
    # Soporte para Usuario Invitado (Sin Registro) con Carro Temporal
    es_invitado = models.BooleanField(
        default=False,
        verbose_name="¿Es Arriendo de Invitado (Sin Registro)?"
    )
    nombre_cliente = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nombre o Razón Social (Invitado)"
    )
    rut_cliente = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="RUT Empresa / Persona (Invitado)"
    )
    email_cliente = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo Electrónico (Invitado)"
    )
    telefono_cliente = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Teléfono de Contacto (Invitado)"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name="Estado del Contrato"
    )
    monto_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Monto Total Contratado"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )

    class Meta:
        verbose_name = "Contrato de Arriendo"
        verbose_name_plural = "Contratos de Arriendo"
        ordering = ['-fecha_creacion']

    def __str__(self):
        cliente = self.usuario.username if self.usuario else f"{self.nombre_cliente} (Invitado)"
        return f"Contrato #{self.id} - {cliente} [{self.estado}] - ${self.monto_total}"


# ==============================================================================
# BLOQUE 7: MODELO DETALLE CONTRATO (SNAPSHOT HISTÓRICO)
# Congela los precios, garantías, fechas y nombres para auditoría contable.
# ==============================================================================
class DetalleContrato(models.Model):
    """
    Registro histórico inmutable de cada maquinaria dentro de un contrato.
    Garantiza que aumentos de precio o bajas de catálogo posteriores
    no alteren las condiciones pactadas legalmente con el cliente.
    """
    contrato = models.ForeignKey(
        ContratoArriendo,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Contrato Asociado"
    )
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.PROTECT,
        related_name='contratos_historicos',
        verbose_name="Maquinaria de Referencia"
    )
    # Campos congelados (Snapshot histórico)
    nombre_maquinaria = models.CharField(
        max_length=150,
        verbose_name="Nombre del Equipo (Histórico)"
    )
    tarifa_diaria = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Tarifa Diaria Congelada"
    )
    garantia_fija = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Garantía Fija Congelada"
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha Inicio Pactada"
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha Fin Pactada"
    )
    dias_uso = models.PositiveIntegerField(
        verbose_name="Días de Uso Facturados"
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Subtotal Facturado"
    )

    class Meta:
        verbose_name = "Detalle de Contrato"
        verbose_name_plural = "Detalles de Contrato"

    def __str__(self):
        return f"Detalle #{self.id}: {self.nombre_maquinaria} (${self.subtotal})"
