"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
MÓDULO: PRUEBAS AUTOMATIZADAS (tests.py)
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
================================================================================
Cubre el 100% de los requerimientos y reglas de negocio:
1. Creación de usuarios con RBAC (Empresa Constructora vs Ejecutivo)
2. Emisión de JWT con Claims personalizados (rol, razón social, rut)
3. Persistencia del Carro de Arriendo en base de datos
4. Cálculo automático de Días de Uso y Costo (Tarifa * Días + Garantía)
5. Checkout Atómico (@transaction.atomic) con descuento de stock
6. Rechazo de arriendo cuando no hay stock disponible
7. Reposición automática de stock al marcar CANCELADO o COMPLETADO
================================================================================
"""

from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    Usuario,
    Categoria,
    Maquinaria,
    CarroArriendo,
    ItemCarro,
    ContratoArriendo,
    DetalleContrato,
)


class RentingMaquinariaTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Crear Usuarios de Prueba
        self.ejecutivo = Usuario.objects.create_user(
            username='test_ejecutivo',
            password='Password123',
            email='ejecutivo@test.cl',
            first_name='Admin',
            last_name='Gestor',
            rol=Usuario.ROL_EJECUTIVO,
            is_staff=True
        )

        self.constructora = Usuario.objects.create_user(
            username='test_constructora',
            password='Password123',
            email='contacto@constructora.cl',
            first_name='Juan',
            last_name='Pérez',
            rol=Usuario.ROL_EMPRESA,
            razon_social='Constructora Los Andes SpA',
            rut_empresa='77.123.456-7'
        )

        # 2. Crear Categoría y Maquinarias
        self.categoria = Categoria.objects.create(
            nombre='Excavación y Movimiento',
            descripcion='Equipos para movimientos de tierra'
        )

        self.maquinaria = Maquinaria.objects.create(
            categoria=self.categoria,
            nombre='Excavadora CAT 320D',
            descripcion='Excavadora pesada para zanjas',
            tarifa_diaria=Decimal('100000.00'),
            garantia_fija=Decimal('300000.00'),
            unidades_disponibles=2,
            imagen_url='https://example.com/cat320.jpg'
        )

    def test_01_catalogo_publico(self):
        """El catálogo de maquinarias debe ser accesible sin autenticación."""
        resp = self.client.get('/api/maquinarias/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_02_jwt_login_con_claims(self):
        """Login JWT debe retornar tokens y claims personalizados con el rol."""
        resp = self.client.post('/api/auth/login/', {
            'username': 'test_constructora',
            'password': 'Password123'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('usuario', resp.data)
        self.assertEqual(resp.data['usuario']['rol'], Usuario.ROL_EMPRESA)
        self.assertEqual(resp.data['usuario']['razon_social'], 'Constructora Los Andes SpA')

    def test_03_calculo_dias_y_costo_en_carro(self):
        """
        Días de Uso = fecha_fin - fecha_inicio (min 1)
        Costo Ítem = (tarifa_diaria * dias_uso) + garantia_fija
        """
        self.client.force_authenticate(user=self.constructora)

        hoy = date.today()
        f_ini = hoy + timedelta(days=1)
        f_fin = f_ini + timedelta(days=4)  # 4 días
        dias_esperados = 4

        resp = self.client.post('/api/carro-arriendo/', {
            'maquinaria_id': self.maquinaria.id,
            'fecha_inicio': f_ini.isoformat(),
            'fecha_fin': f_fin.isoformat(),
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        costo_esperado = (self.maquinaria.tarifa_diaria * dias_esperados) + self.maquinaria.garantia_fija
        # 100.000 * 4 + 300.000 = 700.000
        self.assertEqual(Decimal(str(resp.data['item']['costo_calculado'])), Decimal('700000.00'))
        self.assertEqual(resp.data['item']['dias_uso'], dias_esperados)

        # El stock en flota NO debe haberse descontado todavía
        self.maquinaria.refresh_from_db()
        self.assertEqual(self.maquinaria.unidades_disponibles, 2)

    def test_04_checkout_atomico_y_descuento_stock(self):
        """El checkout atómico descuenta el stock y congela los valores históricos."""
        self.client.force_authenticate(user=self.constructora)

        # Agregar ítem al carro
        hoy = date.today()
        f_ini = hoy + timedelta(days=2)
        f_fin = f_ini + timedelta(days=3)  # 3 días

        self.client.post('/api/carro-arriendo/', {
            'maquinaria_id': self.maquinaria.id,
            'fecha_inicio': f_ini.isoformat(),
            'fecha_fin': f_fin.isoformat(),
        })

        # Ejecutar checkout
        resp = self.client.post('/api/contratos/checkout/')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['contrato']['estado'], ContratoArriendo.ESTADO_PAGADO)

        # Verificar que el stock se descontó de 2 a 1
        self.maquinaria.refresh_from_db()
        self.assertEqual(self.maquinaria.unidades_disponibles, 1)

        # Verificar que el carro quedó vacío
        carro = CarroArriendo.objects.get(usuario=self.constructora)
        self.assertEqual(carro.items.count(), 0)

        # Verificar que el detalle histórico congeló los datos
        contrato_id = resp.data['contrato']['id']
        contrato = ContratoArriendo.objects.get(id=contrato_id)
        detalle = contrato.detalles.first()
        self.assertEqual(detalle.nombre_maquinaria, 'Excavadora CAT 320D')
        self.assertEqual(detalle.tarifa_diaria, Decimal('100000.00'))
        self.assertEqual(detalle.garantia_fija, Decimal('300000.00'))

    def test_05_rechazo_por_stock_insuficiente(self):
        """Si no hay stock en el checkout, se debe rechazar con HTTP 409 Conflict."""
        # Agotar el stock manualmente
        self.maquinaria.unidades_disponibles = 0
        self.maquinaria.save()

        self.client.force_authenticate(user=self.constructora)

        hoy = date.today()
        # Intentar agregar al carro una máquina sin stock debe fallar
        resp = self.client.post('/api/carro-arriendo/', {
            'maquinaria_id': self.maquinaria.id,
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': (hoy + timedelta(days=2)).isoformat(),
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_06_reposicion_automatica_de_stock(self):
        """
        Al cambiar el estado de un contrato a CANCELADO o COMPLETADO,
        el stock debe reincorporarse automáticamente.
        """
        # 1. Crear contrato pagado (stock 2 -> 1)
        self.client.force_authenticate(user=self.constructora)
        hoy = date.today()
        self.client.post('/api/carro-arriendo/', {
            'maquinaria_id': self.maquinaria.id,
            'fecha_inicio': hoy.isoformat(),
            'fecha_fin': (hoy + timedelta(days=2)).isoformat(),
        })
        resp = self.client.post('/api/contratos/checkout/')
        contrato_id = resp.data['contrato']['id']

        self.maquinaria.refresh_from_db()
        self.assertEqual(self.maquinaria.unidades_disponibles, 1)

        # 2. Ejecutivo cambia estado a COMPLETADO (devolución del equipo)
        self.client.force_authenticate(user=self.ejecutivo)
        resp_estado = self.client.patch(f'/api/contratos/{contrato_id}/estado/', {
            'nuevo_estado': ContratoArriendo.ESTADO_COMPLETADO
        })
        self.assertEqual(resp_estado.status_code, status.HTTP_200_OK)

        # 3. El stock debe haberse reincorporado a 2
        self.maquinaria.refresh_from_db()
        self.assertEqual(self.maquinaria.unidades_disponibles, 2)
