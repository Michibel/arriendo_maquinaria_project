"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
MÓDULO: CONTROLADORES Y VISTAS DRF (views.py)
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
================================================================================
Implementa la lógica de negocio, endpoints REST, control de acceso RBAC
y transaccionalidad atómica (@transaction.atomic) para:
1. Autenticación y Emisión de JWT con Claims
2. CRUD de Categorías y Catálogo de Maquinarias (Filtros en tiempo real)
3. Carro de Arriendo Persistente en PostgreSQL
4. Checkout Atómico con Validación y Descuento de Stock
5. Gestión de Contratos y Reposición Automática de Flota
6. Vistas Web para renderizar las interfaces HTML5 / Bootstrap 5
================================================================================
"""

from decimal import Decimal
from datetime import date, datetime, timedelta
from django.db import transaction
from django.db.models import Sum, Count, Avg, F, Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import (
    Usuario,
    Categoria,
    Maquinaria,
    CarroArriendo,
    ItemCarro,
    ContratoArriendo,
    DetalleContrato,
)
from .serializers import (
    CustomTokenObtainPairSerializer,
    UsuarioSerializer,
    RegistroUsuarioSerializer,
    CategoriaSerializer,
    MaquinariaSerializer,
    ItemCarroSerializer,
    ItemCarroCreateSerializer,
    CarroArriendoSerializer,
    ContratoArriendoSerializer,
    DetalleContratoSerializer,
    CambioEstadoContratoSerializer,
    CheckoutInvitadoSerializer,
)
from .permissions import (
    EsEjecutivoDeArriendos,
    EsEmpresaConstructora,
    EsEjecutivoOReadOnly,
)

User = get_user_model()


# ==============================================================================
# BLOQUE 1: VISTAS DE AUTENTICACIÓN Y USUARIO
# ==============================================================================
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint POST /api/auth/login/
    Emite el par de tokens JWT (access y refresh) con claims personalizados
    de rol, razón social y rut de empresa.
    """
    serializer_class = CustomTokenObtainPairSerializer


class RegistroUsuarioView(generics.CreateAPIView):
    """
    Endpoint POST /api/auth/register/
    Permite el registro de nuevos usuarios en el sistema con asignación
    de rol (Empresa Constructora o Ejecutivo).
    """
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]


class PerfilUsuarioView(generics.RetrieveAPIView):
    """
    Endpoint GET /api/auth/me/
    Retorna el perfil del usuario autenticado actual.
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ==============================================================================
# BLOQUE 2: VISTAS DE CATEGORÍA Y MAQUINARIA (CATÁLOGO)
# ==============================================================================
class CategoriaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Categorías.
    Público para lectura (GET); restringido a Ejecutivos para modificaciones.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsEjecutivoOReadOnly]


class MaquinariaViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de Maquinarias.
    - Público: Consulta del catálogo (GET /api/maquinarias/) con filtros en tiempo real
    - Ejecutivo de Arriendos: Creación, actualización y eliminación (POST/PUT/DELETE)
    """
    queryset = Maquinaria.objects.select_related('categoria').all()
    serializer_class = MaquinariaSerializer
    permission_classes = [EsEjecutivoOReadOnly]

    def get_queryset(self):
        """
        Filtros en tiempo real por categoría, rango de tarifas y disponibilidad.
        """
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria')
        disponible = self.request.query_params.get('disponible')
        tarifa_min = self.request.query_params.get('tarifa_min')
        tarifa_max = self.request.query_params.get('tarifa_max')
        busqueda = self.request.query_params.get('search')

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if disponible in ['true', '1', 'True']:
            queryset = queryset.filter(unidades_disponibles__gt=0)
        if tarifa_min:
            queryset = queryset.filter(tarifa_diaria__gte=tarifa_min)
        if tarifa_max:
            queryset = queryset.filter(tarifa_diaria__lte=tarifa_max)
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(descripcion__icontains=busqueda)
            )

        return queryset


# ==============================================================================
# BLOQUE 3: VISTAS DEL CARRO DE ARRIENDO (PERSISTENTE EN POSTGRESQL)
# ==============================================================================
class CarroArriendoView(APIView):
    """
    Endpoint para gestionar el Carro de Arriendo persistente del usuario.
    GET /api/carro-arriendo/  -> Obtiene el carro y su desglose completo
    POST /api/carro-arriendo/ -> Agrega una máquina al carro con cálculo automático
    """
    permission_classes = [permissions.IsAuthenticated, EsEmpresaConstructora]

    def get_carro(self, user):
        carro, _ = CarroArriendo.objects.get_or_create(usuario=user)
        return carro

    def get(self, request):
        carro = self.get_carro(request.user)
        serializer = CarroArriendoSerializer(carro)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        carro = self.get_carro(request.user)
        serializer = ItemCarroCreateSerializer(data=request.data)
        if serializer.is_valid():
            maquinaria = serializer.validated_data['maquinaria']
            fecha_inicio = serializer.validated_data['fecha_inicio']
            fecha_fin = serializer.validated_data['fecha_fin']

            # Verifica si el equipo ya está en el carro para actualizar fechas o agregar
            item_existente = ItemCarro.objects.filter(carro=carro, maquinaria=maquinaria).first()
            if item_existente:
                item_existente.fecha_inicio = fecha_inicio
                item_existente.fecha_fin = fecha_fin
                item_existente.save()
                item_serializer = ItemCarroSerializer(item_existente)
                return Response({
                    'mensaje': f"Arriendo de '{maquinaria.nombre}' actualizado con éxito.",
                    'item': item_serializer.data,
                    'carro': CarroArriendoSerializer(carro).data
                }, status=status.HTTP_200_OK)

            nuevo_item = ItemCarro(
                carro=carro,
                maquinaria=maquinaria,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            nuevo_item.save()
            item_serializer = ItemCarroSerializer(nuevo_item)
            return Response({
                'mensaje': f"'{maquinaria.nombre}' agregada al carro exitosamente.",
                'item': item_serializer.data,
                'carro': CarroArriendoSerializer(carro).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarroItemEliminarView(APIView):
    """
    Endpoint DELETE /api/carro-arriendo/{item_id}/
    Elimina un ítem específico del carro persistente.
    """
    permission_classes = [permissions.IsAuthenticated, EsEmpresaConstructora]

    def delete(self, request, item_id):
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        item = get_object_or_404(ItemCarro, id=item_id, carro=carro)
        nombre = item.maquinaria.nombre
        item.delete()
        return Response({
            'mensaje': f"'{nombre}' eliminada del carro.",
            'carro': CarroArriendoSerializer(carro).data
        }, status=status.HTTP_200_OK)


class CarroVaciarView(APIView):
    """
    Endpoint POST /api/carro-arriendo/vaciar/
    Vacía todos los ítems del carro persistente del usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsEmpresaConstructora]

    def post(self, request):
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        carro.items.all().delete()
        return Response({
            'mensaje': "El carro ha sido vaciado correctamente.",
            'carro': CarroArriendoSerializer(carro).data
        }, status=status.HTTP_200_OK)


# ==============================================================================
# BLOQUE 4: CHECKOUT ATÓMICO, GESTIÓN DE STOCK Y REPOSICIÓN DE FLOTA
# ==============================================================================
class CheckoutContratoView(APIView):
    """
    Endpoint POST /api/contratos/checkout/
    Regla de Negocio Crítica:
    - Se ejecuta bajo @transaction.atomic para garantizar integridad absoluta.
    - El stock NO se descuenta al agregar al carro. Se descuenta únicamente al pagar.
    - Si al momento del checkout alguna maquinaria ya no tiene stock disponible,
      la transacción completa se revierte (rollback) y se rechaza la operación.
    - Se congelan los precios, garantías y fechas en DetalleContrato.
    - Se vacía el carro persistente del usuario.
    """
    permission_classes = [permissions.IsAuthenticated, EsEmpresaConstructora]

    @transaction.atomic
    def post(self, request):
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        items = list(carro.items.select_related('maquinaria').all())

        if not items:
            return Response(
                {'error': "El carro de arriendo se encuentra vacío."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Validación de disponibilidad de stock para todos los ítems antes de proceder
        for item in items:
            # Bloqueo select_for_update para evitar condiciones de carrera en alta concurrencia
            maq = Maquinaria.objects.select_for_update().get(id=item.maquinaria_id)
            if maq.unidades_disponibles < 1:
                # Transacción abortada automáticamente
                return Response({
                    'error': f"Stock insuficiente para '{maq.nombre}'. No hay unidades disponibles en flota."
                }, status=status.HTTP_409_CONFLICT)

        # 2. Creación del Contrato de Arriendo en estado PAGADO
        monto_total_contrato = sum(item.costo_calculado for item in items)
        contrato = ContratoArriendo.objects.create(
            usuario=request.user,
            estado=ContratoArriendo.ESTADO_PAGADO,
            monto_total=monto_total_contrato
        )

        # 3. Creación del Snapshot Histórico (DetalleContrato) y Descuento Atómico de Stock
        for item in items:
            maq = Maquinaria.objects.select_for_update().get(id=item.maquinaria_id)
            
            # Descuento atómico del stock en flota
            maq.unidades_disponibles -= 1
            maq.save()

            # Congelamiento de datos históricos
            DetalleContrato.objects.create(
                contrato=contrato,
                maquinaria=maq,
                nombre_maquinaria=maq.nombre,
                tarifa_diaria=maq.tarifa_diaria,
                garantia_fija=maq.garantia_fija,
                fecha_inicio=item.fecha_inicio,
                fecha_fin=item.fecha_fin,
                dias_uso=item.dias_uso,
                subtotal=item.costo_calculado
            )

        # 4. Vaciar el carro persistente del usuario tras el pago exitoso
        carro.items.all().delete()

        serializer = ContratoArriendoSerializer(contrato)
        return Response({
            'mensaje': "¡Contrato de arriendo generado y pagado exitosamente!",
            'contrato': serializer.data
        }, status=status.HTTP_201_CREATED)


class CheckoutInvitadoView(APIView):
    """
    Endpoint POST /api/contratos/checkout-invitado/
    Permite a un usuario INVITADO (no registrado) finalizar y pagar su arriendo.
    Regla de Negocio:
    - No exige autenticación ni contraseña (sin registro).
    - El carro del invitado es TEMPORAL (almacenado en el cliente) y NO se persiste en PostgreSQL.
    - Se validan y solicitan los datos de contacto: nombre, RUT, email y teléfono.
    - Se procesa bajo @transaction.atomic verificando y descontando el stock en flota.
    - Se genera el ContratoArriendo (es_invitado=True) y su snapshot en DetalleContrato.
    """
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutInvitadoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data
        items_data = datos['items']

        # 1. Validación de stock con select_for_update para todos los ítems
        maquinarias_dict = {}
        for it in items_data:
            maq_id = it['maquinaria_id']
            try:
                maq = Maquinaria.objects.select_for_update().get(id=maq_id)
            except Maquinaria.DoesNotExist:
                return Response({'error': f"Maquinaria con ID {maq_id} no existe."}, status=status.HTTP_404_NOT_FOUND)

            if maq.unidades_disponibles < 1:
                return Response({
                    'error': f"Stock insuficiente para '{maq.nombre}'. No hay unidades disponibles en flota."
                }, status=status.HTTP_409_CONFLICT)
            maquinarias_dict[maq_id] = maq

        # 2. Calcular montos y días
        monto_total_contrato = Decimal('0.00')
        detalles_data = []

        for it in items_data:
            maq = maquinarias_dict[it['maquinaria_id']]
            f_ini = it['fecha_inicio']
            f_fin = it['fecha_fin']
            dias_uso = max(1, (f_fin - f_ini).days)

            tarifa_total = maq.tarifa_diaria * Decimal(dias_uso)
            costo_item = tarifa_total + maq.garantia_fija
            monto_total_contrato += costo_item

            detalles_data.append({
                'maquinaria': maq,
                'nombre_maquinaria': maq.nombre,
                'tarifa_diaria': maq.tarifa_diaria,
                'garantia_fija': maq.garantia_fija,
                'fecha_inicio': f_ini,
                'fecha_fin': f_fin,
                'dias_uso': dias_uso,
                'subtotal': costo_item,
            })

        # 3. Crear Contrato de Arriendo en estado PAGADO con bandera es_invitado=True
        contrato = ContratoArriendo.objects.create(
            usuario=None,
            es_invitado=True,
            nombre_cliente=datos['nombre_cliente'],
            rut_cliente=datos['rut_cliente'],
            email_cliente=datos['email_cliente'],
            telefono_cliente=datos['telefono_cliente'],
            estado=ContratoArriendo.ESTADO_PAGADO,
            monto_total=monto_total_contrato
        )

        # 4. Descuento atómico de stock y creación de DetalleContrato congelado
        for d in detalles_data:
            maq = d['maquinaria']
            maq.unidades_disponibles -= 1
            maq.save()

            DetalleContrato.objects.create(
                contrato=contrato,
                maquinaria=maq,
                nombre_maquinaria=d['nombre_maquinaria'],
                tarifa_diaria=d['tarifa_diaria'],
                garantia_fija=d['garantia_fija'],
                fecha_inicio=d['fecha_inicio'],
                fecha_fin=d['fecha_fin'],
                dias_uso=d['dias_uso'],
                subtotal=d['subtotal']
            )

        resp_serializer = ContratoArriendoSerializer(contrato)
        return Response({
            'mensaje': "¡Arriendo confirmado y pagado exitosamente en modalidad invitado!",
            'contrato': resp_serializer.data
        }, status=status.HTTP_201_CREATED)


class MisContratosListView(generics.ListAPIView):
    """
    Endpoint GET /api/mis-contratos/
    Retorna el historial de contratos y órdenes del cliente autenticado.
    """
    serializer_class = ContratoArriendoSerializer
    permission_classes = [permissions.IsAuthenticated, EsEmpresaConstructora]

    def get_queryset(self):
        return ContratoArriendo.objects.filter(
            usuario=self.request.user
        ).prefetch_related('detalles').order_views() if hasattr(ContratoArriendo.objects, 'order_views') else ContratoArriendo.objects.filter(
            usuario=self.request.user
        ).prefetch_related('detalles').order_by('-fecha_creacion')


class ContratoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Gestión de Contratos de Arriendo para el Ejecutivo de Arriendos.
    - GET /api/contratos/: Lista todos los contratos de todas las constructoras.
    - GET /api/contratos/{id}/: Detalle específico.
    - PATCH /api/contratos/{id}/estado/: Transición de estados con reposición automática de stock.
    """
    queryset = ContratoArriendo.objects.select_related('usuario').prefetch_related('detalles').all()
    serializer_class = ContratoArriendoSerializer
    permission_classes = [EsEjecutivoDeArriendos]

    @action(detail=True, methods=['patch'], url_path='estado')
    def cambiar_estado(self, request, pk=None):
        """
        PATCH /api/contratos/{id}/estado/
        Control de Ciclo de Vida y Flota:
        - Si pasa a COMPLETADO (devolución del equipo) o CANCELADO:
          Se reincorporan automáticamente las unidades a la flota disponible.
        - Si pasa de PENDIENTE a PAGADO:
          Se valida y descuenta el stock de manera atómica.
        """
        contrato = self.get_object()
        serializer = CambioEstadoContratoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        nuevo_estado = serializer.validated_data['nuevo_estado']
        estado_anterior = contrato.estado

        if nuevo_estado == estado_anterior:
            return Response({
                'mensaje': f"El contrato ya se encuentra en estado '{nuevo_estado}'."
            }, status=status.HTTP_200_OK)

        with transaction.atomic():
            detalles = contrato.detalles.select_related('maquinaria').all()

            # Caso 1: Cancelación o Devolución (COMPLETADO / CANCELADO) -> Reposición de stock
            estados_con_stock_descontado = [
                ContratoArriendo.ESTADO_PAGADO,
                ContratoArriendo.ESTADO_ENTREGADO
            ]
            if estado_anterior in estados_con_stock_descontado and nuevo_estado in [
                ContratoArriendo.ESTADO_COMPLETADO,
                ContratoArriendo.ESTADO_CANCELADO
            ]:
                for det in detalles:
                    maq = Maquinaria.objects.select_for_update().get(id=det.maquinaria_id)
                    maq.unidades_disponibles += 1
                    maq.save()

            # Caso 2: Pase tardío de PENDIENTE a PAGADO -> Descuento atómico
            elif estado_anterior == ContratoArriendo.ESTADO_PENDIENTE and nuevo_estado == ContratoArriendo.ESTADO_PAGADO:
                for det in detalles:
                    maq = Maquinaria.objects.select_for_update().get(id=det.maquinaria_id)
                    if maq.unidades_disponibles < 1:
                        return Response({
                            'error': f"No se puede confirmar el pago: Sin stock para '{maq.nombre}'."
                        }, status=status.HTTP_409_CONFLICT)
                    maq.unidades_disponibles -= 1
                    maq.save()

            # Actualización del estado
            contrato.estado = nuevo_estado
            contrato.save()

        return Response({
            'mensaje': f"Estado del contrato #{contrato.id} actualizado a '{nuevo_estado}' correctamente.",
            'contrato': ContratoArriendoSerializer(contrato).data
        }, status=status.HTTP_200_OK)


# ==============================================================================
# BLOQUE 4.1: ENDPOINT DEL DASHBOARD EJECUTIVO (ESTADÍSTICAS AVANZADAS)
# Cosas más vendidas, producción mensual, comparaciones mensuales y trimestrales
# ==============================================================================
class DashboardStatsView(APIView):
    """
    Endpoint GET /api/dashboard/stats/
    Exclusivo para el Ejecutivo de Arriendos.
    Genera métricas consolidadas en tiempo real:
    - KPIs globales (Total facturado, arriendos activos, ticket promedio, ocupación)
    - Cosas más vendidas / más arrendadas (Top maquinarias por frecuencia y recaudación)
    - Producción mensual (Ingresos y contratos mes a mes)
    - Comparación mensual (Mes actual vs Mes anterior con variación %)
    - Comparación trimestral (Q1, Q2, Q3, Q4 con análisis comparativo)
    """
    permission_classes = [permissions.IsAuthenticated, EsEjecutivoDeArriendos]

    def get(self, request):
        now = timezone.now()
        current_year = now.year
        current_month = now.month

        # Contratos válidos (excluyendo cancelados para facturación real)
        contratos_validos = ContratoArriendo.objects.exclude(estado=ContratoArriendo.ESTADO_CANCELADO)
        todos_contratos = ContratoArriendo.objects.all()

        # 1. KPIs Globales
        total_ingresos = contratos_validos.aggregate(total=Sum('monto_total'))['total'] or Decimal('0.00')
        total_contratos_count = todos_contratos.count()
        arriendos_activos = ContratoArriendo.objects.filter(
            estado__in=[ContratoArriendo.ESTADO_PAGADO, ContratoArriendo.ESTADO_ENTREGADO]
        ).count()
        ticket_promedio = (total_ingresos / Decimal(contratos_validos.count())) if contratos_validos.count() > 0 else Decimal('0.00')

        total_flota = Maquinaria.objects.aggregate(total=Sum('unidades_disponibles'))['total'] or 0
        total_equipos_arrendados = DetalleContrato.objects.filter(
            contrato__estado__in=[ContratoArriendo.ESTADO_PAGADO, ContratoArriendo.ESTADO_ENTREGADO]
        ).count()
        total_capacidad = total_flota + total_equipos_arrendados
        tasa_ocupacion = round((total_equipos_arrendados / total_capacidad * 100), 1) if total_capacidad > 0 else 0.0

        # 2. Cosas más vendidas / más arrendadas (Top Maquinarias)
        top_items = (
            DetalleContrato.objects
            .exclude(contrato__estado=ContratoArriendo.ESTADO_CANCELADO)
            .values('maquinaria__id', 'maquinaria__nombre', 'maquinaria__imagen_url', 'maquinaria__categoria__nombre', 'maquinaria__tarifa_diaria')
            .annotate(
                total_arriendos=Count('id'),
                total_dias=Sum('dias_uso'),
                total_facturado=Sum('subtotal')
            )
            .order_by('-total_arriendos', '-total_facturado')[:6]
        )

        mas_vendidos = [
            {
                'id': item['maquinaria__id'],
                'nombre': item['maquinaria__nombre'],
                'categoria': item['maquinaria__categoria__nombre'] or 'Maquinaria',
                'imagen_url': item['maquinaria__imagen_url'] or '',
                'tarifa_diaria': float(item['maquinaria__tarifa_diaria'] or 0),
                'total_arriendos': item['total_arriendos'],
                'total_dias': item['total_dias'] or 0,
                'total_facturado': float(item['total_facturado'] or 0),
            }
            for item in top_items
        ]

        # 3. Producción Mensual (Mes a Mes del año en curso)
        nombres_meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        produccion_mensual = []
        for m in range(1, 13):
            qs_mes = contratos_validos.filter(fecha_creacion__year=current_year, fecha_creacion__month=m)
            ingresos_m = qs_mes.aggregate(tot=Sum('monto_total'))['tot'] or Decimal('0.00')
            contratos_m = qs_mes.count()
            produccion_mensual.append({
                'mes_numero': m,
                'mes_nombre': nombres_meses[m - 1],
                'mes_corto': nombres_meses[m - 1][:3],
                'ingresos': float(ingresos_m),
                'contratos': contratos_m,
            })

        # 4. Comparación Mensual (Mes Actual vs Mes Anterior)
        prev_month = 12 if current_month == 1 else current_month - 1
        prev_year = current_year - 1 if current_month == 1 else current_year

        qs_actual = contratos_validos.filter(fecha_creacion__year=current_year, fecha_creacion__month=current_month)
        qs_anterior = contratos_validos.filter(fecha_creacion__year=prev_year, fecha_creacion__month=prev_month)

        ingresos_actual = qs_actual.aggregate(tot=Sum('monto_total'))['tot'] or Decimal('0.00')
        ingresos_anterior = qs_anterior.aggregate(tot=Sum('monto_total'))['tot'] or Decimal('0.00')
        contratos_actual = qs_actual.count()
        contratos_anterior = qs_anterior.count()

        if ingresos_anterior > 0:
            var_ingresos_pct = round(((ingresos_actual - ingresos_anterior) / ingresos_anterior) * 100, 1)
        else:
            var_ingresos_pct = 100.0 if ingresos_actual > 0 else 0.0

        if contratos_anterior > 0:
            var_contratos_pct = round(((contratos_actual - contratos_anterior) / contratos_anterior) * 100, 1)
        else:
            var_contratos_pct = 100.0 if contratos_actual > 0 else 0.0

        comparacion_mensual = {
            'mes_actual': nombres_meses[current_month - 1],
            'mes_anterior': nombres_meses[prev_month - 1],
            'ingresos_actual': float(ingresos_actual),
            'ingresos_anterior': float(ingresos_anterior),
            'variacion_ingresos_pct': float(var_ingresos_pct),
            'contratos_actual': contratos_actual,
            'contratos_anterior': contratos_anterior,
            'variacion_contratos_pct': float(var_contratos_pct),
        }

        # 5. Comparación Trimestral (Q1, Q2, Q3, Q4)
        trimestres_def = [
            ('Q1 (Ene-Mar)', [1, 2, 3]),
            ('Q2 (Abr-Jun)', [4, 5, 6]),
            ('Q3 (Jul-Sep)', [7, 8, 9]),
            ('Q4 (Oct-Dic)', [10, 11, 12]),
        ]
        comparacion_trimestral = []
        for nombre_q, meses_q in trimestres_def:
            qs_q = contratos_validos.filter(fecha_creacion__year=current_year, fecha_creacion__month__in=meses_q)
            ingresos_q = qs_q.aggregate(tot=Sum('monto_total'))['tot'] or Decimal('0.00')
            contratos_q = qs_q.count()
            comparacion_trimestral.append({
                'trimestre': nombre_q,
                'ingresos': float(ingresos_q),
                'contratos': contratos_q,
            })

        return Response({
            'kpis': {
                'total_ingresos': float(total_ingresos),
                'total_contratos': total_contratos_count,
                'arriendos_activos': arriendos_activos,
                'ticket_promedio': float(ticket_promedio),
                'total_flota': total_flota,
                'tasa_ocupacion': tasa_ocupacion,
            },
            'mas_vendidos': mas_vendidos,
            'produccion_mensual': produccion_mensual,
            'comparacion_mensual': comparacion_mensual,
            'comparacion_trimestral': comparacion_trimestral,
        }, status=status.HTTP_200_OK)


# ==============================================================================
# BLOQUE 5: VISTAS DEL FRONTEND WEB (HTML5 / BOOTSTRAP 5)
# Renderizan las plantillas integradas con datos y el footer institucional.
# ==============================================================================
def catalogo_view(request):
    """Vista principal: Catálogo interactivo de maquinarias."""
    return render(request, 'catalogo.html')

def carro_view(request):
    """Vista del Carro de Arriendos persistente y resumen de costos."""
    return render(request, 'carro.html')

def mis_contratos_view(request):
    """Vista del historial de contratos del cliente."""
    return render(request, 'mis_contratos.html')

def panel_ejecutivo_view(request):
    """Vista del panel de administración para el Ejecutivo de Arriendos."""
    return render(request, 'panel_ejecutivo.html')

def login_view(request):
    """Vista dedicada de autenticación y registro."""
    return render(request, 'login.html')
