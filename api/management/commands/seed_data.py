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
        # 4. CREACIÓN DE CONTRATOS HISTÓRICOS PARA DASHBOARD ANALÍTICO
        # Distribuidos en Q1, Q2, Q3 y mes actual para graficar producción y comparativas
        # ----------------------------------------------------------------------
        from django.utils import timezone
        import datetime

        # Eliminar contratos previos para regenerar métricas limpias
        ContratoArriendo.objects.all().delete()

        # Maquinarias clave
        cat320 = Maquinaria.objects.get(nombre='Excavadora Hidráulica CAT 320D')
        jcb = Maquinaria.objects.get(nombre='Retroexcavadora JCB 3CX Eco')
        bobcat = Maquinaria.objects.get(nombre='Minicargador Bobcat S570')
        genie = Maquinaria.objects.get(nombre='Plataforma Tijera Genie GS-2646')
        toyota = Maquinaria.objects.get(nombre='Grúa Horquilla Toyota Tonero 3.0T')
        dynapac = Maquinaria.objects.get(nombre='Rodillo Compactador Dynapac CA250D')
        cat140m = Maquinaria.objects.get(nombre='Motoniveladora Caterpillar 140M')
        pramac = Maquinaria.objects.get(nombre='Generador Diésel Pramac GSW 110 kVA')

        # Definición de contratos con fechas específicas de 2026
        escenarios_contratos = [
            # Q1: Enero, Febrero, Marzo
            {'user': constructora1, 'fecha': datetime.date(2026, 1, 15), 'items': [(cat320, 6), (bobcat, 4)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 1, 28), 'items': [(jcb, 5)], 'estado': 'COMPLETADO'},
            {'user': constructora1, 'fecha': datetime.date(2026, 2, 10), 'items': [(cat320, 8), (pramac, 8)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 2, 22), 'items': [(toyota, 12)], 'estado': 'COMPLETADO'},
            {'user': constructora1, 'fecha': datetime.date(2026, 3, 5),  'items': [(dynapac, 7), (cat140m, 5)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 3, 18), 'items': [(cat320, 10), (jcb, 7)], 'estado': 'COMPLETADO'},

            # Q2: Abril, Mayo, Junio
            {'user': constructora1, 'fecha': datetime.date(2026, 4, 12), 'items': [(genie, 15), (toyota, 8)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 4, 25), 'items': [(bobcat, 6), (jcb, 4)], 'estado': 'COMPLETADO'},
            {'user': constructora1, 'fecha': datetime.date(2026, 5, 8),  'items': [(cat320, 12), (dynapac, 9)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 5, 20), 'items': [(cat140m, 8)], 'estado': 'COMPLETADO'},
            {'user': constructora1, 'fecha': datetime.date(2026, 6, 14), 'items': [(pramac, 10), (jcb, 6)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 6, 27), 'items': [(cat320, 14), (bobcat, 7)], 'estado': 'COMPLETADO'},

            # Q3: Julio, Agosto, Septiembre (Mes Actual y Anterior)
            {'user': constructora1, 'fecha': datetime.date(2026, 7, 10), 'items': [(toyota, 10), (genie, 8)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 7, 24), 'items': [(jcb, 9), (bobcat, 5)], 'estado': 'COMPLETADO'},
            {'user': constructora1, 'fecha': datetime.date(2026, 8, 11), 'items': [(cat320, 15), (pramac, 12)], 'estado': 'COMPLETADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 8, 25), 'items': [(dynapac, 10), (cat140m, 6)], 'estado': 'COMPLETADO'},
            # Mes Actual: Septiembre
            {'user': constructora1, 'fecha': datetime.date(2026, 9, 5),  'items': [(cat320, 18), (jcb, 10)], 'estado': 'PAGADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 9, 14), 'items': [(bobcat, 12), (toyota, 8)], 'estado': 'ENTREGADO'},
            {'user': constructora1, 'fecha': datetime.date(2026, 9, 22), 'items': [(cat320, 10), (dynapac, 8)], 'estado': 'PAGADO'},
            {'user': constructora2, 'fecha': datetime.date(2026, 9, 28), 'items': [(genie, 7)], 'estado': 'PENDIENTE'},
        ]

        total_contratos_creados = 0
        for esc in escenarios_contratos:
            f_emision = esc['fecha']
            items_list = esc['items']
            estado_c = esc['estado']

            # Calcular total
            monto_total = Decimal('0.00')
            detalles_a_crear = []
            for maq, dias in items_list:
                sub = (maq.tarifa_diaria * dias) + maq.garantia_fija
                monto_total += sub
                f_ini = f_emision + datetime.timedelta(days=1)
                f_fin = f_ini + datetime.timedelta(days=dias)
                detalles_a_crear.append({
                    'maquinaria': maq,
                    'nombre': maq.nombre,
                    'tarifa': maq.tarifa_diaria,
                    'garantia': maq.garantia_fija,
                    'f_ini': f_ini,
                    'f_fin': f_fin,
                    'dias': dias,
                    'subtotal': sub
                })

            contrato = ContratoArriendo.objects.create(
                usuario=esc['user'],
                estado=estado_c,
                monto_total=monto_total
            )

            # Forzar fecha de creación histórica para las comparativas temporales
            dt_creacion = timezone.make_aware(datetime.datetime.combine(f_emision, datetime.time(10, 30)))
            ContratoArriendo.objects.filter(id=contrato.id).update(fecha_creacion=dt_creacion)

            for d in detalles_a_crear:
                DetalleContrato.objects.create(
                    contrato=contrato,
                    maquinaria=d['maquinaria'],
                    nombre_maquinaria=d['nombre'],
                    tarifa_diaria=d['tarifa'],
                    garantia_fija=d['garantia'],
                    fecha_inicio=d['f_ini'],
                    fecha_fin=d['f_fin'],
                    dias_uso=d['dias'],
                    subtotal=d['subtotal']
                )

            total_contratos_creados += 1

        self.stdout.write(self.style.SUCCESS(f"[OK] {total_contratos_creados} Contratos analíticos generados para el Dashboard."))
        self.stdout.write(self.style.SUCCESS("=== BASE DE DATOS POBLADA EXITOSAMENTE CON DASHBOARD EJECUTIVO ==="))
