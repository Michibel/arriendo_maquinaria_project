"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN
COMANDO DE GESTIÓN: POBLAR BASE DE DATOS (seed_data.py)
Autor: Gabriel Michibel | Sección: DGY2102 | Año: 2026
================================================================================
Ejecutar con: python manage.py seed_data
Puebla la base de datos PostgreSQL con:
1. Usuarios de prueba (Ejecutivo de Arriendos y Empresas Constructoras)
2. Familias y Categorías de Maquinaria
3. Maquinarias con tarifas diarias, garantías y stock real
4. Contratos de muestra en diferentes estados para validar el frontend
================================================================================
"""

from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import (
    Usuario,
    Categoria,
    Maquinaria,
    CarroArriendo,
    ContratoArriendo,
    DetalleContrato,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Puebla la base de datos con datos de prueba industriales y usuarios con roles RBAC."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando carga de datos semilla para el Proyecto 6..."))

        # ----------------------------------------------------------------------
        # 1. CREACIÓN DE USUARIOS
        # ----------------------------------------------------------------------
        # Superuser / Ejecutivo de Arriendos
        ejecutivo, creado = Usuario.objects.get_or_create(
            username='ejecutivo',
            defaults={
                'email': 'ejecutivo@rentamaq.cl',
                'first_name': 'Gabriel',
                'last_name': 'Michibel',
                'rol': Usuario.ROL_EJECUTIVO,
                'razon_social': 'RentaMaq Industrial SpA',
                'rut_empresa': '76.999.888-1',
                'telefono': '+56 9 9123 4567',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if creado:
            ejecutivo.set_password('admin123')
            ejecutivo.save()
            CarroArriendo.objects.get_or_create(usuario=ejecutivo)
            self.stdout.write(self.style.SUCCESS("[OK] Usuario Ejecutivo creado: 'ejecutivo' / 'admin123'"))

        # Cliente 1: Empresa Constructora
        constructora1, creado = Usuario.objects.get_or_create(
            username='constructora_vial',
            defaults={
                'email': 'contacto@vialsurchile.cl',
                'first_name': 'Roberto',
                'last_name': 'Gómez',
                'rol': Usuario.ROL_EMPRESA,
                'razon_social': 'Constructora Vial del Sur SpA',
                'rut_empresa': '77.892.450-K',
                'telefono': '+56 9 8765 4321',
            }
        )
        if creado:
            constructora1.set_password('123456')
            constructora1.save()
            CarroArriendo.objects.get_or_create(usuario=constructora1)
            self.stdout.write(self.style.SUCCESS("[OK] Usuario Constructora 1 creado: 'constructora_vial' / '123456'"))
        
        # Cliente 2: Ingeniería y Minería
        constructora2, creado = Usuario.objects.get_or_create(
            username='ingenieria_andina',
            defaults={
                'email': 'adquisiciones@andinaobras.cl',
                'first_name': 'Camila',
                'last_name': 'Navarro',
                'rol': Usuario.ROL_EMPRESA,
                'razon_social': 'Ingeniería Andina & Obras Civiles S.A.',
                'rut_empresa': '76.432.100-8',
                'telefono': '+56 9 7654 3210',
            }
        )
        if creado:
            constructora2.set_password('123456')
            constructora2.save()
            CarroArriendo.objects.get_or_create(usuario=constructora2)
            self.stdout.write(self.style.SUCCESS("[OK] Usuario Constructora 2 creado: 'ingenieria_andina' / '123456'"))

        # ----------------------------------------------------------------------
        # 2. CREACIÓN DE CATEGORÍAS
        # ----------------------------------------------------------------------
        categorias_data = [
            {
                'nombre': 'Movimiento de Tierras y Excavación',
                'descripcion': 'Maquinaria pesada para excavación profunda, terraplenes y demolición.'
            },
            {
                'nombre': 'Elevación y Trabajo en Altura',
                'descripcion': 'Equipos hidráulicos de izaje seguro, plataformas tijera y grúas telescópicas.'
            },
            {
                'nombre': 'Compactación y Asfalto',
                'descripcion': 'Rodillos vibratorios y equipos de alisado para caminos y bases de pavimentación.'
            },
            {
                'nombre': 'Carga y Transporte en Faena',
                'descripcion': 'Minicargadores versátiles y camiones tolva para acopio de áridos.'
            },
            {
                'nombre': 'Generación Eléctrica e Iluminación',
                'descripcion': 'Grupos electrógenos insonorizados y torres solares para faenas nocturnas.'
            },
        ]

        categorias_map = {}
        for c in categorias_data:
            obj, _ = Categoria.objects.get_or_create(
                nombre=c['nombre'],
                defaults={'descripcion': c['descripcion']}
            )
            categorias_map[c['nombre']] = obj
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(categorias_map)} Categorías sincronizadas."))

        # ----------------------------------------------------------------------
        # 3. CREACIÓN DE MAQUINARIAS
        # ----------------------------------------------------------------------
        maquinarias_data = [
            {
                'categoria': categorias_map['Movimiento de Tierras y Excavación'],
                'nombre': 'Excavadora Hidráulica CAT 320D',
                'descripcion': 'Potente excavadora de 20 toneladas con balde de 1.2 m³. Ideal para zanjas masivas, canteras y movimientos de tierra exigentes.',
                'tarifa_diaria': Decimal('165000.00'),
                'garantia_fija': Decimal('550000.00'),
                'unidades_disponibles': 4,
                'imagen_url': 'https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=800&q=80',
            },
            {
                'categoria': categorias_map['Movimiento de Tierras y Excavación'],
                'nombre': 'Retroexcavadora JCB 3CX Eco',
                'descripcion': 'Equipo multipropósito 4x4 con brazo extensible y pala cargadora frontal de 1 m³. Operación ágil en faenas urbanas e industriales.',
                'tarifa_diaria': Decimal('98000.00'),
                'garantia_fija': Decimal('320000.00'),
                'unidades_disponibles': 5,
                'imagen_url': 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80',
            },
            {
                'categoria': categorias_map['Carga y Transporte en Faena'],
                'nombre': 'Minicargador Bobcat S570',
                'descripcion': 'Minicargador compacto con sistema hidráulico de alto flujo y cabina presurizada. Maniobrabilidad precisa en espacios confinados.',
                'tarifa_diaria': Decimal('68000.00'),
                'garantia_fija': Decimal('220000.00'),
                'unidades_disponibles': 6,
                'imagen_url': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80',
            },
            {
                'categoria': categorias_map['Elevación y Trabajo en Altura'],
                'nombre': 'Plataforma Tijera Genie GS-2646',
                'descripcion': 'Elevador eléctrico para trabajos en altura hasta 10 metros, capacidad 454 kg. Cero emisiones, óptimo para interiores de galpones.',
                'tarifa_diaria': Decimal('52000.00'),
                'garantia_fija': Decimal('160000.00'),
                'unidades_disponibles': 3,
                'imagen_url': 'https://images.unsplash.com/photo-1541888946425-d0fbb186c5f7?auto=format&fit=crop&w=800&q=80',
            },
            {
                'categoria': categorias_map['Elevación y Trabajo en Altura'],
                'nombre': 'Grúa Horquilla Toyota Tonero 3.0T',
                'descripcion': 'Autoelevador diésel de 3.0 toneladas con mástil triplex de 4.8 metros. Robusto y con cabina ergonómica SAS.',
                'tarifa_diaria': Decimal('58000.00'),
                'garantia_fija': Decimal('190000.00'),
                'unidades_disponibles': 4,
                'imagen_url': 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80',
            },
            {
                'categoria': categorias_map['Compactación y Asfalto'],
                'nombre': 'Rodillo Compactador Dynapac CA250D',
                'descripcion': 'Rodillo vibratorio monocilíndrico de 11 toneladas para compactación profunda de bases granulares y terraplenes viales.',
                'tarifa_diaria': Decimal('125000.00'),
                'garantia_fija': Decimal('380000.00'),
                'unidades_disponibles': 2,
                'imagen_url': 'https://images.unsplash.com/photo-1517581177682-a085bb7ffb15?auto=format&fit=crop&w=800&q=80',
            },
            {
                'categoria': categorias_map['Compactación y Asfalto'],
                'nombre': 'Motoniveladora Caterpillar 140M',
                'descripcion': 'Motoniveladora de alta precisión con vertedera de 3.7 metros y tracción total para perfilado y mantenimiento de rutas.',
                'tarifa_diaria': Decimal('195000.00'),
                'garantia_fija': Decimal('650000.00'),
                'unidades_disponibles': 2,
                'imagen_url': 'https://images.unsplash.com/photo-1587293852726-70cdb56c2866?auto=format&fit=crop&w=800&q=80',
            },
            {
                'categoria': categorias_map['Generación Eléctrica e Iluminación'],
                'nombre': 'Generador Diésel Pramac GSW 110 kVA',
                'descripcion': 'Grupo electrógeno insonorizado con motor Volvo e interruptor de transferencia automática (ATS). Autonomía de 14 horas continuas.',
                'tarifa_diaria': Decimal('82000.00'),
                'garantia_fija': Decimal('260000.00'),
                'unidades_disponibles': 5,
                'imagen_url': 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=800&q=80',
            },
        ]

        for m in maquinarias_data:
            Maquinaria.objects.get_or_create(
                nombre=m['nombre'],
                defaults=m
            )
        self.stdout.write(self.style.SUCCESS(f"[OK] {len(maquinarias_data)} Maquinarias cargadas en catálogo."))

        # ----------------------------------------------------------------------
        # 4. CREACIÓN DE CONTRATOS HISTÓRICOS DE MUESTRA
        # ----------------------------------------------------------------------
        maq1 = Maquinaria.objects.get(nombre='Retroexcavadora JCB 3CX Eco')
        maq2 = Maquinaria.objects.get(nombre='Minicargador Bobcat S570')

        if not ContratoArriendo.objects.filter(usuario=constructora1).exists():
            hoy = date.today()
            f_inicio = hoy + timedelta(days=2)
            f_fin = f_inicio + timedelta(days=5)
            dias = 5
            
            subtotal1 = (maq1.tarifa_diaria * dias) + maq1.garantia_fija
            subtotal2 = (maq2.tarifa_diaria * dias) + maq2.garantia_fija
            total = subtotal1 + subtotal2

            contrato = ContratoArriendo.objects.create(
                usuario=constructora1,
                estado=ContratoArriendo.ESTADO_PAGADO,
                monto_total=total
            )

            DetalleContrato.objects.create(
                contrato=contrato,
                maquinaria=maq1,
                nombre_maquinaria=maq1.nombre,
                tarifa_diaria=maq1.tarifa_diaria,
                garantia_fija=maq1.garantia_fija,
                fecha_inicio=f_inicio,
                fecha_fin=f_fin,
                dias_uso=dias,
                subtotal=subtotal1
            )
            DetalleContrato.objects.create(
                contrato=contrato,
                maquinaria=maq2,
                nombre_maquinaria=maq2.nombre,
                tarifa_diaria=maq2.tarifa_diaria,
                garantia_fija=maq2.garantia_fija,
                fecha_inicio=f_inicio,
                fecha_fin=f_fin,
                dias_uso=dias,
                subtotal=subtotal2
            )
            # Descontar stock correspondiente a este contrato pagado
            maq1.unidades_disponibles -= 1
            maq1.save()
            maq2.unidades_disponibles -= 1
            maq2.save()

            self.stdout.write(self.style.SUCCESS(f"[OK] Contrato de demostración #{contrato.id} creado para '{constructora1.username}'"))

        self.stdout.write(self.style.SUCCESS("=== BASE DE DATOS POBLADA EXITOSAMENTE ==="))
