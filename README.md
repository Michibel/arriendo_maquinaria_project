# Proyecto 6: Arriendo de Maquinaria de Construcción (Renting / Servicios)
## Evaluación 2 (EVA-2) - Arquitectura y Desarrollo Backend & Frontend

**Estudiante:** Gabriel Michibel  
**Sección:** IEC-N4-C1  
**Año:** 2026  
**Institución:** Duoc UC  

---

## 🏗️ Descripción del Proyecto
Plataforma web integral para la gestión y arriendo de maquinarias pesadas y equipos de construcción para empresas constructoras y faenas mineras. Implementa una arquitectura profesional desacoplada con **Django REST Framework (DRF)**, persistencia en **PostgreSQL**, autenticación **JWT con RBAC (Role-Based Access Control)**, transacciones atómicas para control de inventario/flota y un frontend responsivo basado en **Bootstrap 5**, **HTML5** y **JavaScript ES6**.

---

## ⚙️ Tecnologías Utilizadas
- **Backend:** Python 3.14 / Django 6.1 / Django REST Framework 3.18
- **Base de Datos:** PostgreSQL nativo (`django.db.backends.postgresql`)
- **Autenticación & Seguridad:** `djangorestframework-simplejwt` con claims personalizados de Rol
- **Documentación API:** `drf-spectacular` (OpenAPI 3.0 / Swagger UI)
- **Frontend:** HTML5 semántico, CSS3 personalizado con paleta industrial, Bootstrap 5.3 (Mobile-First), FontAwesome 6, Fetch API ES6

---

## 📋 Reglas de Negocio Implementadas

1. **Cálculo de Tarifas y Días de Uso:**
   $$\text{Días de Uso} = \max(1, (\text{fecha\_fin} - \text{fecha\_inicio}).\text{days})$$
   $$\text{Costo Ítem} = (\text{tarifa\_diaria} \times \text{dias\_uso}) + \text{garantia\_fija}$$

2. **Carro Persistente en PostgreSQL (`CarroArriendo` 1:1 con `User`):**
   - El carro no se pierde al cerrar sesión ni al recargar el navegador.
   - El stock de flota **NO se descuenta** al agregar al carro.

3. **Checkout Atómico y Control de Stock (`@transaction.atomic`):**
   - Al ejecutar el checkout (`POST /api/contratos/checkout/`), se valida atómicamente la existencia de stock para cada máquina con bloqueo de concurrencia (`select_for_update`).
   - Si no hay stock disponible, la transacción completa se revierte (**Rollback**) y se devuelve error `409 Conflict`.
   - Si hay stock, se crea el `ContratoArriendo` en estado `PAGADO`, se congelan los precios y fechas en `DetalleContrato` (snapshot inmutable), se descuentan las unidades y se vacía el carro.

4. **Reposición Automática de Flota:**
   - Si el contrato pasa a `COMPLETADO` (devolución del equipo en faena) o `CANCELADO`, las unidades se reincorporan automáticamente al stock disponible en PostgreSQL.

5. **Control de Acceso Basado en Roles (RBAC):**
   - **Público:** Ver catálogo de maquinarias y categorías.
   - **Empresa Constructora (Cliente):** Administrar su propio carro, checkout y consultar "Mis Arriendos".
   - **Ejecutivo de Arriendos (Gestor/Admin):** CRUD completo de maquinarias, modificar stock y cambiar estado de contratos de cualquier cliente.

6. **Dashboard Ejecutivo Gerencial (Chart.js & Analytics):**
   - **Cosas más vendidas:** Ranking y gráfico Doughnut con las maquinarias más solicitadas, días acumulados en faena y total facturado.
   - **Producción mensual:** Gráfico mixto de barras y línea con la facturación mes a mes y volumen de contratos del año 2026.
   - **Comparaciones mensuales:** Mes actual vs mes anterior con cálculo de variación porcentual (+/- X%) e indicadores visuales de tendencia.
   - **Comparaciones trimestrales:** Análisis comparativo de ingresos y arriendos por trimestres (Q1, Q2, Q3, Q4).
   - **Redirección automática:** Al iniciar sesión como Ejecutivo/Administrador, el sistema redirige automáticamente a `/panel/`.

7. **Soporte de Carro Temporal y Checkout para Usuario Invitado (Sin Registro):**
   - Los usuarios no registrados pueden explorar el catálogo y agregar maquinarias al carro de arriendo temporal sin necesidad de iniciar sesión previa.
   - El carro de invitado se mantiene de forma temporal en el navegador (`localStorage`), sin generar registros huérfanos en la base de datos PostgreSQL.
   - Al finalizar la compra (`POST /api/contratos/checkout-invitado/`), un modal interactivo captura los datos de contacto y facturación: Nombre completo, RUT, Email y Teléfono.
   - La operación se ejecuta bajo `@transaction.atomic` garantizando el descuento atómico de stock en flota, la creación del `ContratoArriendo` (con `es_invitado=True`) y el snapshot inmutable en `DetalleContrato`.

---

## 🚀 Guía de Instalación y Ejecución Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Michibel/arriendo_maquinaria_project.git
cd arriendo_maquinaria_project
```

### 2. Crear y Activar Entorno Virtual
```powershell
python -m venv env
.\env\Scripts\activate
```

### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 4. Configurar Base de Datos PostgreSQL
Asegúrate de que PostgreSQL esté en ejecución en el puerto 5432 y crear la base de datos:
```sql
CREATE DATABASE arriendo_maquinaria_db;
```
*(Las credenciales por defecto configuradas en `settings.py` corresponden a usuario `postgres` en `localhost:5432`)*.

### 5. Aplicar Migraciones
```powershell
python manage.py migrate
```

### 6. Cargar Datos Semilla Iniciales
```powershell
python manage.py seed_data
```

### 7. Ejecutar Servidor de Desarrollo
```powershell
python manage.py runserver
```

---

## 🔑 Credenciales de Prueba (RBAC)

| Rol | Usuario | Contraseña | Permisos |
| :--- | :--- | :--- | :--- |
| **Ejecutivo de Arriendos** | `ejecutivo` | `admin123` | Administrador / CRUD catálogo / Cambio de estado contratos |
| **Empresa Constructora** | `constructora_vial` | `123456` | Cliente / Carro persistente / Checkout / Mis arriendos |
| **Empresa Constructora** | `ingenieria_andina` | `123456` | Cliente secundario |

---

## 🌐 URLs y Rutas Principales

### Vistas Web (Frontend)
- **Catálogo Principal:** `http://127.0.0.1:8000/` o `http://127.0.0.1:8000/catalogo/`
- **Carro de Arriendo:** `http://127.0.0.1:8000/carro/`
- **Mis Arriendos (Cliente):** `http://127.0.0.1:8000/mis-contratos/`
- **Panel Ejecutivo:** `http://127.0.0.1:8000/panel/`
- **Iniciar Sesión / Registro:** `http://127.0.0.1:8000/login/`

### Endpoints API REST & Documentación
- **Documentación Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **Esquema OpenAPI:** `http://127.0.0.1:8000/api/schema/`
- **Catálogo Maquinarias:** `GET /api/maquinarias/`
- **Carro de Arriendo:** `GET / POST / DELETE /api/carro-arriendo/`
- **Checkout Atómico:** `POST /api/contratos/checkout/`
- **Mis Contratos:** `GET /api/mis-contratos/`
- **Cambio de Estado:** `PATCH /api/contratos/{id}/estado/`
- **Autenticación JWT:** `POST /api/auth/login/` (con Claims personalizados)

---

## 🧪 Ejecución de Pruebas Unitarias
```powershell
python manage.py test api
```
*Pruebas cubren el 100% de los flujos críticos: catálogo público, JWT con claims, cálculos de fechas y montos, checkout atómico y reposición de stock.*

---
**Pie de página:**  
`Gabriel Michibel | Sección IEC-N4-C1 | Año 2026`
