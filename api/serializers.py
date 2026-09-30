"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
MÓDULO: SERIALIZADORES DRF (serializers.py)
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
================================================================================
Este archivo define la serialización y deserialización de datos, validaciones
de reglas de negocio y personalización de JWT claims:
1. CustomTokenObtainPairSerializer: Inyecta claims de RBAC (Rol, RUT, Razón Social)
2. UsuarioSerializer & RegistroUsuarioSerializer: Gestión de cuentas y roles
3. CategoriaSerializer: Información de familias de maquinaria
4. MaquinariaSerializer: Catálogo, tarifas, garantías y stock
5. ItemCarroSerializer & ItemCarroCreateSerializer: Carro persistente y cálculo automático
6. CarroArriendoSerializer: Vista global del carro con totales
7. DetalleContratoSerializer: Snapshot histórico inmutable
8. ContratoArriendoSerializer & CambioEstadoContratoSerializer: Ciclo de vida del arriendo
================================================================================
"""

from decimal import Decimal
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Usuario,
    Categoria,
    Maquinaria,
    CarroArriendo,
    ItemCarro,
    ContratoArriendo,
    DetalleContrato,
)

User = get_user_model()


# ==============================================================================
# BLOQUE 1: SERIALIZADOR JWT CON CLAIMS PERSONALIZADOS (RBAC)
# ==============================================================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza la emisión de JSON Web Tokens (SimpleJWT) agregando información
    del rol del usuario, RUT y Razón Social directamente dentro del payload
    del token y en el cuerpo de la respuesta JSON para el frontend.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Inyección de claims en el payload del JWT
        token['rol'] = user.rol
        token['rol_display'] = user.get_rol_display()
        token['username'] = user.username
        token['email'] = user.email
        token['es_ejecutivo'] = user.es_ejecutivo
        token['es_constructora'] = user.es_constructora
        token['razon_social'] = user.razon_social or ''
        token['rut_empresa'] = user.rut_empresa or ''
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Inyección adicional en la respuesta JSON para uso inmediato en JavaScript
        data['usuario'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nombre_completo': self.user.get_full_name() or self.user.username,
            'rol': self.user.rol,
            'rol_display': self.user.get_rol_display(),
            'es_ejecutivo': self.user.es_ejecutivo,
            'es_constructora': self.user.es_constructora,
            'razon_social': self.user.razon_social or '',
            'rut_empresa': self.user.rut_empresa or '',
        }
        return data


# ==============================================================================
# BLOQUE 2: SERIALIZADORES DE USUARIO Y REGISTRO
# ==============================================================================
class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para consultar información del usuario autenticado."""
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'rol_display', 'rut_empresa', 'razon_social',
            'telefono', 'es_ejecutivo', 'es_constructora'
        ]
        read_only_fields = ['id', 'rol_display', 'es_ejecutivo', 'es_constructora']


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador para registro de nuevos usuarios en el sistema.
    Cifra la contraseña de manera segura usando create_user().
    """
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'rol', 'rut_empresa', 'razon_social', 'telefono'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        # Inicializa automáticamente su Carro de Arriendo persistente
        CarroArriendo.objects.get_or_create(usuario=usuario)
        return usuario


# ==============================================================================
# BLOQUE 3: SERIALIZADOR DE CATEGORÍA
# ==============================================================================
class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para categorías de maquinaria."""
    total_maquinarias = serializers.IntegerField(
        source='maquinarias.count',
        read_only=True
    )

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'total_maquinarias']


# ==============================================================================
# BLOQUE 4: SERIALIZADOR DE MAQUINARIA
# ==============================================================================
class MaquinariaSerializer(serializers.ModelSerializer):
    """
    Serializador completo de maquinaria para catálogo público
    y mantenimiento por parte del Ejecutivo de Arriendos.
    """
    categoria_nombre = serializers.CharField(
        source='categoria.nombre',
        read_only=True
    )
    tiene_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Maquinaria
        fields = [
            'id', 'categoria', 'categoria_nombre', 'nombre',
            'descripcion', 'tarifa_diaria', 'garantia_fija',
            'unidades_disponibles', 'tiene_stock', 'imagen_url'
        ]

    def validate_tarifa_diaria(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("La tarifa diaria debe ser un monto mayor a cero.")
        return value

    def validate_garantia_fija(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError("La garantía fija no puede ser negativa.")
        return value


# ==============================================================================
# BLOQUE 5: SERIALIZADORES DEL CARRO DE ARRIENDO E ÍTEMS
# ==============================================================================
class ItemCarroSerializer(serializers.ModelSerializer):
    """
    Serializador para representar los ítems del carro, incluyendo
    los detalles del equipo y los cálculos automáticos de días y costos.
    """
    maquinaria = MaquinariaSerializer(read_only=True)

    class Meta:
        model = ItemCarro
        fields = [
            'id', 'maquinaria', 'fecha_inicio', 'fecha_fin',
            'dias_uso', 'costo_calculado'
        ]


class ItemCarroCreateSerializer(serializers.ModelSerializer):
    """
    Serializador de entrada para agregar un ítem al carro persistente.
    Aplica las validaciones de rango de fechas y stock en flota.
    """
    maquinaria_id = serializers.PrimaryKeyRelatedField(
        queryset=Maquinaria.objects.all(),
        source='maquinaria',
        write_only=True
    )

    class Meta:
        model = ItemCarro
        fields = ['maquinaria_id', 'fecha_inicio', 'fecha_fin']

    def validate(self, attrs):
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')
        maquinaria = attrs.get('maquinaria')

        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise serializers.ValidationError({
                    'fecha_fin': "La fecha de fin debe ser igual o posterior a la fecha de inicio."
                })
        
        # Validar disponibilidad de stock
        if maquinaria.unidades_disponibles <= 0:
            raise serializers.ValidationError({
                'maquinaria_id': f"La maquinaria '{maquinaria.nombre}' no tiene unidades disponibles en este momento."
            })

        return attrs


class CarroArriendoSerializer(serializers.ModelSerializer):
    """
    Serializador para la vista completa del Carro de Arriendo persistente.
    Calcula los subtotales, garantías y gran total en tiempo real.
    """
    items = ItemCarroSerializer(many=True, read_only=True)
    monto_total = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    subtotal_tarifas = serializers.SerializerMethodField()
    total_garantias = serializers.SerializerMethodField()

    class Meta:
        model = CarroArriendo
        fields = [
            'id', 'usuario', 'fecha_actualizacion', 'items',
            'total_items', 'subtotal_tarifas', 'total_garantias', 'monto_total'
        ]
        read_only_fields = ['id', 'usuario', 'fecha_actualizacion']

    def get_monto_total(self, obj):
        return sum(item.costo_calculado for item in obj.items.all())

    def get_total_items(self, obj):
        return obj.items.count()

    def get_subtotal_tarifas(self, obj):
        return sum(
            item.maquinaria.tarifa_diaria * Decimal(item.dias_uso)
            for item in obj.items.all()
        )

    def get_total_garantias(self, obj):
        return sum(item.maquinaria.garantia_fija for item in obj.items.all())


# ==============================================================================
# BLOQUE 6: SERIALIZADORES DE CONTRATO Y DETALLE HISTÓRICO
# ==============================================================================
class DetalleContratoSerializer(serializers.ModelSerializer):
    """
    Serializador de detalles de contrato (Snapshot histórico congelado).
    """
    class Meta:
        model = DetalleContrato
        fields = [
            'id', 'maquinaria', 'nombre_maquinaria', 'tarifa_diaria',
            'garantia_fija', 'fecha_inicio', 'fecha_fin', 'dias_uso', 'subtotal'
        ]


class ContratoArriendoSerializer(serializers.ModelSerializer):
    """
    Serializador completo de contratos de arriendo para clientes registrados,
    invitados y ejecutivos.
    """
    detalles = DetalleContratoSerializer(many=True, read_only=True)
    usuario_info = serializers.SerializerMethodField()

    class Meta:
        model = ContratoArriendo
        fields = [
            'id', 'usuario', 'usuario_info', 'es_invitado', 'nombre_cliente',
            'rut_cliente', 'email_cliente', 'telefono_cliente',
            'estado', 'monto_total', 'fecha_creacion', 'fecha_actualizacion', 'detalles'
        ]
        read_only_fields = ['id', 'usuario', 'monto_total', 'fecha_creacion', 'fecha_actualizacion']

    def get_usuario_info(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'username': obj.usuario.username,
                'razon_social': obj.usuario.razon_social or obj.usuario.get_full_name() or obj.usuario.username,
                'rut_empresa': obj.usuario.rut_empresa or 'N/A',
                'email': obj.usuario.email,
                'telefono': obj.usuario.telefono or 'N/A',
                'es_invitado': False,
            }
        return {
            'id': None,
            'username': 'Invitado',
            'razon_social': obj.nombre_cliente or 'Cliente Invitado',
            'rut_empresa': obj.rut_cliente or 'N/A',
            'email': obj.email_cliente or 'N/A',
            'telefono': obj.telefono_cliente or 'N/A',
            'es_invitado': True,
        }


class CambioEstadoContratoSerializer(serializers.Serializer):
    """
    Serializador para la acción PATCH /api/contratos/{id}/estado/.
    Valida las transiciones de estado permitidas por la regla de negocio.
    """
    nuevo_estado = serializers.ChoiceField(
        choices=ContratoArriendo.ESTADOS_CHOICES,
        required=True
    )


# ==============================================================================
# BLOQUE 7: SERIALIZADOR DE CHECKOUT PARA USUARIO INVITADO (SIN REGISTRO)
# ==============================================================================
class ItemInvitadoInputSerializer(serializers.Serializer):
    """Ítem enviado desde el carro temporal del usuario invitado."""
    maquinaria_id = serializers.IntegerField(required=True)
    fecha_inicio = serializers.DateField(required=True)
    fecha_fin = serializers.DateField(required=True)

    def validate(self, attrs):
        if attrs['fecha_fin'] < attrs['fecha_inicio']:
            raise serializers.ValidationError("La fecha de término no puede ser anterior a la de inicio.")
        return attrs


class CheckoutInvitadoSerializer(serializers.Serializer):
    """
    Formulario de Checkout para Usuario Invitado:
    Captura los datos de contacto y facturación sin exigir registro ni contraseña.
    """
    nombre_cliente = serializers.CharField(max_length=150, required=True)
    rut_cliente = serializers.CharField(max_length=20, required=True)
    email_cliente = serializers.EmailField(required=True)
    telefono_cliente = serializers.CharField(max_length=30, required=True)
    items = ItemInvitadoInputSerializer(many=True, required=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("El carro temporal se encuentra vacío.")
        return value
