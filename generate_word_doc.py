"""
Script para generar el documento Word (.docx) profesional con toda la
explicación del código del Proyecto 6: Arriendo de Maquinaria de Construcción.
Autor: Gabriel Michibel | Sección: IEC-N4-C1 | Año: 2026
"""

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    """Asigna color de fondo hexadecimal a una celda de tabla."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Asigna márgenes internos (padding) a una celda."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_callout(doc, text, title="NOTA TÉCNICA", border_color="D97706", bg_color="FEF3C7"):
    """Crea una caja de texto destacada (Callout box)."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Borde izquierdo grueso
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    left_b = OxmlElement('w:left')
    left_b.set(qn('w:val'), 'single')
    left_b.set(qn('w:sz'), '24')
    left_b.set(qn('w:space'), '0')
    left_b.set(qn('w:color'), border_color)
    tcBorders.append(left_b)
    
    for b_name in ['top', 'bottom', 'right']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'none')
        tcBorders.append(b)
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"📌 {title}: ")
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(180, 83, 9)
    
    run_c = p.add_run(text)
    run_c.font.size = Pt(9.5)
    run_c.font.color.rgb = RGBColor(30, 41, 59)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_code_block(doc, code_text):
    """Agrega un bloque de código formateado con fondo gris."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.rows[0].cells[0]
    cell.width = Inches(6.5)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(15, 23, 42)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def build_document():
    doc = Document()
    
    # Configuración de márgenes de página (1 pulgada = 2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
        # Encabezado y Pie de Página
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("Gabriel Michibel | Sección: IEC-N4-C1 | Año 2026 — Proyecto 6: Arriendo de Maquinaria")
        f_run.font.name = "Calibri"
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(100, 116, 139)

    # =========================================================================
    # PORTADA
    # =========================================================================
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)
    p_pre.paragraph_format.space_after = Pt(6)
    run_pre = p_pre.add_run("Inacap Temuco - Ingenieria en Ciberseguridad • ESCUELA DE INFORMÁTICA Y TELECOMUNICACIONES")
    run_pre.font.name = "Arial"
    run_pre.font.size = Pt(11)
    run_pre.font.bold = True
    run_pre.font.color.rgb = RGBColor(180, 83, 9)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(12)
    run_title = p_title.add_run("INFORME TÉCNICO Y EXPLICACIÓN INTEGRAL DE CÓDIGO")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(24)
    run_sub = p_sub.add_run("Proyecto 6: Plataforma Web de Arriendo de Maquinaria de Construcción (Renting / Servicios)")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Línea divisoria
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(28)
    run_div = p_div.add_run("━" * 55)
    run_div.font.color.rgb = RGBColor(217, 119, 6)

    # Tabla de datos institucionales
    meta_table = doc.add_table(rows=7, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    
    meta_data = [
        ("Estudiante:", "Gabriel Michibel"),
        ("Sección Académica:", "IEC-N4-C1"),
        ("Año Académico:", "2026"),
        ("Evaluación:", "Evaluación 2 (EVA-2) — Arquitectura Backend y Frontend Web"),
        ("Stack Tecnológico:", "Python 3.14, Django 6.1, DRF 3.18, PostgreSQL 18, SimpleJWT, Bootstrap 5"),
        ("Repositorio GitHub:", "https://github.com/Michibel/arriendo_maquinaria_project"),
        ("Footer Institucional:", "Gabriel Michibel | Sección IEC-N4-C1 | Año 2026")
    ]
    
    for idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.3)
        set_cell_background(cell_lbl, "F8FAFC")
        set_cell_background(cell_val, "FFFFFF")
        set_cell_margins(cell_lbl, top=60, bottom=60, left=100, right=100)
        set_cell_margins(cell_val, top=60, bottom=60, left=100, right=100)
        
        p0 = cell_lbl.paragraphs[0]
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(30, 41, 59)
        
        p1 = cell_val.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_page_break()

    # =========================================================================
    # ÍNDICE GENERAL
    # =========================================================================
    p_idx_h = doc.add_heading("ÍNDICE DE CONTENIDOS", level=1)
    p_idx_h.paragraph_format.space_before = Pt(12)
    p_idx_h.paragraph_format.space_after = Pt(14)
    
    index_items = [
        "1. Arquitectura General y Stack Tecnológico",
        "2. Seguridad, Autenticación SimpleJWT y Control RBAC",
        "3. Modelo de Datos PostgreSQL e Integridad Relacional (api/models.py)",
        "4. Serializadores, Validaciones y Lógica de Entrada (api/serializers.py)",
        "5. Controladores, Transacciones Atómicas y Reglas de Negocio (api/views.py)",
        "6. Enrutamiento, Fallback y Captura Universal con re_path (urls.py)",
        "7. Frontend Web: Interfaz Dual de Carro y Experiencia de Usuario",
        "8. Batería de Pruebas Automatizadas (api/tests.py)",
        "9. Guía Maestra para la Defensa Individual ante el Docente"
    ]
    for it in index_items:
        p_it = doc.add_paragraph()
        p_it.paragraph_format.space_after = Pt(4)
        run_it = p_it.add_run(f"• {it}")
        run_it.font.size = Pt(10.5)
        run_it.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # =========================================================================
    # CAPÍTULO 1: ARQUITECTURA GENERAL
    # =========================================================================
    doc.add_heading("1. Arquitectura General y Stack Tecnológico", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "El proyecto implementa una Arquitectura en Capas Desacoplada (Cliente-Servidor). "
        "El Backend está construido sobre Django REST Framework (DRF) exponiendo una API RESTful completa "
        "con salida JSON estandarizada y documentación viva Swagger / OpenAPI en /api/docs/. "
        "La persistencia reside en un motor de base de datos relacional PostgreSQL nativo (puerto 5432), "
        "descartando SQLite para garantizar soporte pleno de concurrencia real, bloqueos de fila e integridad ACID."
    )
    
    doc.add_heading("Capas del Sistema:", level=2)
    layers = [
        ("Capa de Presentación (Frontend):", "HTML5 Semántico, CSS3 con tema industrial, Bootstrap 5.3 (Mobile-First) y JavaScript ES6 cliente con Fetch API."),
        ("Capa de Enrutamiento y Despacho:", "arriendo_maquinaria_project/urls.py y api/urls.py encargados del mapeo de vistas, endpoints REST y fallback catch-all."),
        ("Capa de Negocio y Seguridad:", "api/views.py y api/permissions.py que encapsulan validación de tokens JWT, permisos RBAC y transaccionalidad atómica."),
        ("Capa de Transformación y Serialización:", "api/serializers.py responsable de validar datos de entrada, formatear JSON de salida y calcular subtotales."),
        ("Capa de Persistencia y Datos:", "api/models.py acoplado a PostgreSQL nativo mediante el ORM de Django con migraciones versionadas.")
    ]
    for l_title, l_desc in layers:
        p_l = doc.add_paragraph()
        p_l.paragraph_format.space_after = Pt(4)
        r_t = p_l.add_run(f"• {l_title} ")
        r_t.bold = True
        r_t.font.color.rgb = RGBColor(180, 83, 9)
        p_l.add_run(l_desc)

    create_callout(
        doc,
        "La arquitectura desacoplada permite que el frontend consuma exactamente la misma API REST que podría consumir una aplicación móvil nativa (Flutter / React Native) sin modificar una sola línea del backend.",
        "VENTAJA DE LA ARQUITECTURA"
    )

    # =========================================================================
    # CAPÍTULO 2: SEGURIDAD Y JWT
    # =========================================================================
    doc.add_heading("2. Seguridad, Autenticación SimpleJWT y Control RBAC", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "En lugar de depender de sesiones de servidor tradicionales basadas en cookies, la plataforma utiliza "
        "JSON Web Tokens (JWT) mediante djangorestframework-simplejwt. Esto proporciona escalabilidad horizontal sin estado (stateless)."
    )

    doc.add_heading("Claims Personalizados en el Token:", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "Mediante la clase CustomTokenObtainPairSerializer, al momento del inicio de sesión (/api/auth/login/) "
        "se inyectan atributos dentro de la carga útil (payload) del token JWT. Esto permite al cliente conocer el rol y datos "
        "del usuario sin necesidad de realizar peticiones adicionales:"
    )
    
    add_code_block(doc, """class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Inyección de claims personalizados para RBAC
        token['user_id'] = user.id
        token['username'] = user.username
        token['rol'] = user.rol
        token['razon_social'] = user.razon_social or user.get_full_name()
        token['rut_empresa'] = user.rut_empresa
        token['es_ejecutivo'] = user.es_ejecutivo
        token['es_constructora'] = user.es_constructora
        return token""")

    doc.add_heading("Control de Acceso Basado en Roles (RBAC):", level=2)
    rbac_table = doc.add_table(rows=4, cols=3)
    rbac_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Rol / Perfil", "Permisos DRF Aplicados", "Alcance y Operaciones"]
    for i, h in enumerate(headers):
        cell = rbac_table.rows[0].cells[i]
        set_cell_background(cell, "0F172A")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

    rbac_rows = [
        ("Público / Invitado", "AllowAny", "Ver catálogo (/api/maquinarias/), cotizador dinámico y checkout sin registro (/api/contratos/checkout-invitado/)."),
        ("Empresa Constructora", "IsAuthenticated,\nEsEmpresaConstructora", "Gestionar su propio carro persistente (/api/carro-arriendo/), checkout autenticado y consultar historial (/api/mis-contratos/)."),
        ("Ejecutivo de Arriendos", "IsAuthenticated,\nEsEjecutivoDeArriendos", "CRUD de maquinaria y stock, cambiar estado de contratos (/api/contratos/{id}/estado/) y acceder a métricas (/api/dashboard/stats/).")
    ]
    for r_idx, (c0, c1, c2) in enumerate(rbac_rows, start=1):
        row = rbac_table.rows[r_idx]
        for c_idx, text in enumerate([c0, c1, c2]):
            cell = row.cells[c_idx]
            set_cell_background(cell, "F8FAFC" if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(9)
            if c_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # =========================================================================
    # CAPÍTULO 3: MODELOS DE DATOS
    # =========================================================================
    doc.add_heading("3. Modelo de Datos PostgreSQL e Integridad Relacional", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "El esquema relacional fue diseñado para soportar integridad referencial estricta, "
        "persistencia individualizada y congelamiento histórico de transacciones comerciales:"
    )

    models_info = [
        ("Usuario (AbstractUser):", "Extiende la tabla auth_user de Django agregando: rol (EMPRESA_CONSTRUCTORA o EJECUTIVO_ARRIENDOS), razon_social, rut_empresa y telefono."),
        ("Categoria:", "Clasificador industrial (Excavación, Compactación, etc.) con relación PROTECT hacia Maquinaria para impedir borrados accidentales de categorías con flota activa."),
        ("Maquinaria:", "Entidad central de inventario. Campos: categoria (FK), nombre, descripcion, tarifa_diaria (Decimal), garantia_fija (Decimal), unidades_disponibles (stock) e imagen_url."),
        ("CarroArriendo:", "Modelado con OneToOneField con Usuario. Garantiza que cada empresa registrada cuente con un único carro persistente que no se borra al cerrar sesión."),
        ("ItemCarro:", "Relaciona Carro con Maquinaria. En su método save() autocalcula días de uso = max(1, fecha_fin - fecha_inicio) y costo_calculado = (tarifa * dias) + garantia."),
        ("ContratoArriendo:", "Representa la orden formal de arriendo. Campos: usuario (nullable), es_invitado (booleano), estado (PENDIENTE, PAGADO, ENTREGADO, COMPLETADO, CANCELADO), monto_total y fecha_creacion."),
        ("DetalleContrato:", "Snapshot Histórico Inmutable. Clona los precios, garantías y nombres de los equipos al momento exacto de la firma para aislar el contrato de futuras variaciones de catálogo.")
    ]
    for m_t, m_d in models_info:
        p_m = doc.add_paragraph()
        p_m.paragraph_format.space_after = Pt(4)
        r_t = p_m.add_run(f"✓ {m_t} ")
        r_t.bold = True
        r_t.font.color.rgb = RGBColor(15, 23, 42)
        p_m.add_run(m_d)

    create_callout(
        doc,
        "El uso de OneToOneField(User) en CarroArriendo asegura que el usuario autenticado nunca pierda sus cotizaciones. A nivel de base de datos se genera un índice UNIQUE sobre usuario_id.",
        "CONCEPTO CLAVE: PERSISTENCIA 1 A 1"
    )

    # =========================================================================
    # CAPÍTULO 4: SERIALIZADORES
    # =========================================================================
    doc.add_heading("4. Serializadores, Validaciones y Lógica de Entrada", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "En api/serializers.py residen los componentes de validación estricta y transformación bidireccional:"
    )

    serializers_list = [
        ("ItemCarroCreateSerializer:", "Aplica validaciones de negocio previas al guardado: comprueba que fecha_fin sea igual o posterior a fecha_inicio y rechaza de inmediato si la maquinaria no tiene unidades disponibles en flota."),
        ("CarroArriendoSerializer:", "Utiliza SerializerMethodField para calcular en tiempo real subtotal_tarifas, total_garantias y monto_total a partir de todos los ítems vinculados."),
        ("CheckoutInvitadoSerializer:", "Formulario de contacto para arriendos sin registro. Exige nombre_cliente, rut_cliente, email_cliente, telefono_cliente y un array no vacío de items con validación de fechas."),
        ("CambioEstadoContratoSerializer:", "Valida que el nuevo estado enviado por el ejecutivo pertenezca estrictamente al conjunto de choices válidos del modelo.")
    ]
    for s_t, s_d in serializers_list:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(4)
        r_t = p_s.add_run(f"• {s_t} ")
        r_t.bold = True
        r_t.font.color.rgb = RGBColor(217, 119, 6)
        p_s.add_run(s_d)

    # =========================================================================
    # CAPÍTULO 5: CONTROLADORES Y TRANSACCIONALIDAD
    # =========================================================================
    doc.add_heading("5. Controladores, Transacciones Atómicas y Reglas de Negocio", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "En api/views.py se implementan los flujos más críticos de la plataforma. "
        "A continuación se analizan los puntos que el docente evaluará con mayor rigurosidad:"
    )

    doc.add_heading("A. Checkout Atómico y Bloqueo Pesimista (select_for_update):", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "Tanto en el checkout de usuario registrado (CheckoutContratoView) como en el de invitado (CheckoutInvitadoView), "
        "se utiliza el decorador @transaction.atomic junto con select_for_update():"
    )
    
    add_code_block(doc, """@transaction.atomic
def post(self, request):
    # 1. Bloqueo pesimista a nivel de fila en PostgreSQL
    for item in items_carro:
        maq = Maquinaria.objects.select_for_update().get(id=item.maquinaria_id)
        if maq.unidades_disponibles < 1:
            # Rollback automático de la transacción completa
            return Response({'error': f"Stock agotado para {maq.nombre}"}, status=409)
        
        # 2. Descuento efectivo del stock
        maq.unidades_disponibles -= 1
        maq.save()
        
    # 3. Creación del contrato y congelamiento histórico (DetalleContrato)
    contrato = ContratoArriendo.objects.create(...)
    # 4. Vaciado del carro""")

    doc.add_heading("B. Reposición Automática de Flota al Cancelar o Completar:", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "Cuando el ejecutivo despacha o finaliza un arriendo mediante el endpoint PATCH /api/contratos/{id}/estado/, "
        "si el estado pasa a COMPLETADO (devolución del equipo) o CANCELADO, el backend itera automáticamente "
        "los registros de DetalleContrato y ejecuta maq.unidades_disponibles += 1, reincorporando la flota al catálogo."
    )

    doc.add_heading("C. Dashboard Analítico Ejecutivo (DashboardStatsView):", level=2)
    p = doc.add_paragraph()
    p.add_run(
        "El endpoint /api/dashboard/stats/ resuelve métricas gerenciales de alto impacto mediante funciones del ORM de Django:"
    )
    kpis = [
        ("Equipos más solicitados:", "Agrupación con .values('maquinaria__nombre') y agregaciones Count('id') y Sum('subtotal')."),
        ("Producción Mensual:", "Utiliza TruncMonth('fecha_creacion') para agrupar facturación y volumen mes por mes de 2026."),
        ("Comparativa Mensual:", "Cálculo matemático de variación porcentual respecto al mes anterior: ((Actual - Previo) / Previo) * 100."),
        ("Comparativa Trimestral:", "Utiliza ExtractQuarter('fecha_creacion') para consolidar ingresos por trimestre (Q1, Q2, Q3, Q4).")
    ]
    for k_t, k_d in kpis:
        p_k = doc.add_paragraph()
        p_k.paragraph_format.space_after = Pt(3)
        r = p_k.add_run(f"  - {k_t} ")
        r.bold = True
        p_k.add_run(k_d)

    # =========================================================================
    # CAPÍTULO 6: ENRUTAMIENTO Y REPATH
    # =========================================================================
    doc.add_heading("6. Enrutamiento, Fallback y Captura Universal con re_path", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "Para ofrecer una experiencia de usuario fluida y evitar pantallas de error 404, en "
        "arriendo_maquinaria_project/urls.py se implementó una regla de captura universal mediante re_path:"
    )
    
    add_code_block(doc, """from django.urls import path, include, re_path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', web_views.catalogo_view, name='home'),
    path('catalogo/', web_views.catalogo_view, name='catalogo'),
    path('carro/', web_views.carro_view, name='carro'),
    path('mis-contratos/', web_views.mis_contratos_view, name='mis_contratos_web'),
    path('panel/', web_views.panel_ejecutivo_view, name='panel_ejecutivo_web'),
    path('login/', web_views.login_view, name='login_web'),
    path('auth/login/', web_views.login_view, name='login'),

    # CATCH-ALL REPATH: Redirige cualquier link o ruta desconocida al inicio
    re_path(r'^.*$', RedirectView.as_view(pattern_name='home', permanent=False), name='fallback_home'),
]""")

    # =========================================================================
    # CAPÍTULO 7: FRONTEND Y CARRO DUAL
    # =========================================================================
    doc.add_heading("7. Frontend Web: Interfaz Dual de Carro y Experiencia de Usuario", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "La interfaz web fue construida con una arquitectura de Componente JavaScript Dual en static/js/app.js:"
    )

    cart_dual = [
        ("Usuario Registrado (Persistente en PostgreSQL):", "Las acciones de agregar, listar y eliminar equipos consumen los endpoints /api/carro-arriendo/. Los datos sobreviven al cierre de sesión o cambio de dispositivo."),
        ("Usuario Invitado (Temporal en sessionStorage):", "Las cotizaciones se mantienen en la memoria volátil de la pestaña activa (sessionStorage). No se generan registros huérfanos en PostgreSQL y al cerrar el navegador los datos desaparecen completamente."),
        ("Checkout de Invitado con Modal:", "Al presionar pagar, un modal Bootstrap 5 solicita Nombre, RUT, Email y Teléfono, enviándolos al endpoint AllowAny /api/contratos/checkout-invitado/.")
    ]
    for c_t, c_d in cart_dual:
        p_c = doc.add_paragraph()
        p_c.paragraph_format.space_after = Pt(4)
        r = p_c.add_run(f"★ {c_t} ")
        r.bold = True
        r.font.color.rgb = RGBColor(180, 83, 9)
        p_c.add_run(c_d)

    # =========================================================================
    # CAPÍTULO 8: PRUEBAS AUTOMATIZADAS
    # =========================================================================
    doc.add_heading("8. Batería de Pruebas Automatizadas (api/tests.py)", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "Se implementó una suite completa de 8 pruebas unitarias y de integración que certifican "
        "el 100% de cumplimiento de la pauta de evaluación. Ejecución: env\\Scripts\\python manage.py test api"
    )

    tests_table = doc.add_table(rows=9, cols=3)
    tests_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Identificador", "Regla de Negocio Validada", "Resultado"]
    for i, h in enumerate(t_headers):
        cell = tests_table.rows[0].cells[i]
        set_cell_background(cell, "1E293B")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9)

    tests_rows = [
        ("test_01", "Catálogo público accesible sin autenticación (GET /api/maquinarias/)", "APROBADO (OK)"),
        ("test_02", "Login JWT emite access token con claims personalizados (rol, razón social)", "APROBADO (OK)"),
        ("test_03", "Cálculo exacto de días y costo en carro; stock no se descuenta al agregar", "APROBADO (OK)"),
        ("test_04", "Checkout atómico descuenta stock, congela snapshot y vacía carro", "APROBADO (OK)"),
        ("test_05", "Rechazo con HTTP 400/409 cuando se intenta arrendar equipo sin stock", "APROBADO (OK)"),
        ("test_06", "Reposición automática de stock al marcar contrato como COMPLETADO o CANCELADO", "APROBADO (OK)"),
        ("test_07", "Dashboard ejecutivo retorna KPIs, más vendidos y comparativas mensuales", "APROBADO (OK)"),
        ("test_08", "Checkout de usuario invitado sin registro con datos de contacto y descuento atómico", "APROBADO (OK)")
    ]
    for r_idx, (t_id, t_desc, t_res) in enumerate(tests_rows, start=1):
        row = tests_table.rows[r_idx]
        for c_idx, val in enumerate([t_id, t_desc, t_res]):
            cell = row.cells[c_idx]
            set_cell_background(cell, "F1F5F9" if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.bold = True
            if c_idx == 2:
                r.bold = True
                r.font.color.rgb = RGBColor(22, 101, 52)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # =========================================================================
    # CAPÍTULO 9: GUÍA PARA LA DEFENSA ANTE EL DOCENTE
    # =========================================================================
    doc.add_heading("9. Guía Maestra para la Defensa Individual ante el Docente", level=1)
    
    p = doc.add_paragraph()
    p.add_run(
        "A continuación se detallan las respuestas modelo para las preguntas teóricas y prácticas "
        "que el docente realizará durante la defensa oral individual:"
    )

    qa_list = [
        (
            "Pregunta 1: ¿Por qué la base de datos es PostgreSQL nativo y se rechazó SQLite?",
            "Respuesta Modelo: 'Profesor, PostgreSQL es un motor relacional de producción multi-hilo que implementa aislamiento ACID real y soporta bloqueos pesimistas a nivel de fila (SELECT ... FOR UPDATE). SQLite maneja bloqueos a nivel de archivo completo, lo que genera cuellos de botella (database is locked) bajo concurrencia. Además, PostgreSQL posee funciones nativas avanzadas de fechas como TruncMonth y ExtractQuarter que utilizamos para el Dashboard Ejecutivo.'"
        ),
        (
            "Pregunta 2: ¿Dónde viaja el rol del usuario y cómo se validan los permisos?",
            "Respuesta Modelo: 'El rol viaja dentro del payload del JSON Web Token (JWT) codificado en Base64. Al iniciar sesión, CustomTokenObtainPairSerializer inyecta el claim token[\"rol\"]. Cuando el cliente realiza peticiones con el header Authorization: Bearer <token>, el middleware de SimpleJWT autentica al usuario y nuestras clases en permissions.py comprueban si request.user.rol coincide con EJECUTIVO_ARRIENDOS o EMPRESA_CONSTRUCTORA.'"
        ),
        (
            "Pregunta 3: ¿Cómo se garantiza que dos usuarios no arrienden la última máquina al mismo tiempo?",
            "Respuesta Modelo: 'Implementamos control de concurrencia pesimista en views.py. Dentro de un bloque decorado con @transaction.atomic, ejecutamos Maquinaria.objects.select_for_update().get(id=...). Esto le indica a PostgreSQL que reserve la fila hasta que termine la transacción. Si dos usuarios compran al mismo instante, el segundo esperará en cola; cuando el primero compre y reduzca el stock a 0, la validación del segundo fallará y la transacción realizará un Rollback completo devolviendo HTTP 409 Conflict.'"
        ),
        (
            "Pregunta 4: ¿Por qué el carro de invitados usa sessionStorage y no localStorage?",
            "Respuesta Modelo: 'Porque localStorage almacena datos permanentemente en el disco del cliente, lo que violaría el requerimiento de que el carro de invitado sea estrictamente temporal y no persistente. Con sessionStorage, los datos existen únicamente mientras la pestaña del navegador está activa; al cerrar la pestaña o ventana, los ítems se destruyen automáticamente sin dejar registros huérfanos en PostgreSQL.'"
        ),
        (
            "Pregunta 5: ¿Qué utilidad tiene la tabla DetalleContrato si ya tenemos Maquinaria?",
            "Respuesta Modelo: 'Representa el concepto de Snapshot Histórico Inmutable. Si un cliente arrienda una grúa a $100.000 CLP y el próximo mes la empresa sube la tarifa a $180.000 CLP, los contratos firmados en el pasado no deben alterarse. DetalleContrato congela la tarifa, garantía y nombre vigentes en Pesos Chilenos (CLP) al segundo exacto de la transacción.'"
        )
    ]

    for q, a in qa_list:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(3)
        r_q = p_q.add_run(q)
        r_q.bold = True
        r_q.font.size = Pt(10.5)
        r_q.font.color.rgb = RGBColor(180, 83, 9)

        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_after = Pt(8)
        r_a = p_a.add_run(a)
        r_a.font.size = Pt(10)
        r_a.font.color.rgb = RGBColor(30, 41, 59)

    # Pie final
    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(24)
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nDOCUMENTO TÉCNICO OFICIAL — PROYECTO 6 ARRIENDO DE MAQUINARIA\nGabriel Michibel | Sección IEC-N4-C1 | Año 2026")
    r_end.font.size = Pt(9)
    r_end.font.color.rgb = RGBColor(148, 163, 184)

    # Guardar archivo
    output_filename = "Explicacion_Completa_Proyecto_Arriendo_Maquinaria.docx"
    doc.save(output_filename)
    print(f"[OK] Documento generado exitosamente como '{output_filename}'")

if __name__ == "__main__":
    build_document()
