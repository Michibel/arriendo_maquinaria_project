"""
================================================================================
PROYECTO 6: ARRIENDO DE MAQUINARIA DE CONSTRUCCIÓN (RENTING / SERVICIOS)
EVALUACIÓN 2 - DESARROLLO BACKEND & FRONTEND WEB
Estudiante: Gabriel Michibel | Sección: DGY2102 | Año: 2026
Base de Datos: PostgreSQL Nativo (puerto 5432)
================================================================================
"""

from pathlib import Path
from datetime import timedelta
import os

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta para desarrollo
SECRET_KEY = 'django-insecure-arriendo-maquinaria-eva2-duoc-2026-secret-key-michibel'

# Modo depuración activo en entorno formativo
DEBUG = True

ALLOWED_HOSTS = ['*']

# ==============================================================================
# APLICACIONES INSTALADAS
# ==============================================================================
INSTALLED_APPS = [
    # Aplicaciones nativas de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías de terceros requeridas en la pauta de evaluación
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'corsheaders',

    # Aplicación principal del sistema
    'api.apps.ApiConfig',
]

# ==============================================================================
# MODELO DE USUARIO PERSONALIZADO (RBAC)
# ==============================================================================
AUTH_USER_MODEL = 'api.Usuario'

# ==============================================================================
# MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Soporte CORS para consumo frontend
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'arriendo_maquinaria_project.urls'

# ==============================================================================
# PLANTILLAS HTML Y CONTEXT PROCESSORS
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Context processor para asegurar el footer requerido por la pauta
                'api.context_processors.datos_alumno_footer',
            ],
        },
    },
]

WSGI_APPLICATION = 'arriendo_maquinaria_project.wsgi.application'

# ==============================================================================
# BASE DE DATOS: POSTGRESQL NATIVO (django.db.backends.postgresql)
# No se permite SQLite según la pauta de evaluación.
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'arriendo_maquinaria_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Lolito01'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ==============================================================================
# VALIDADORES DE CONTRASEÑA
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 4},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# INTERNACIONALIZACIÓN Y ZONA HORARIA
# ==============================================================================
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES)
# ==============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# CONFIGURACIÓN DJANGO REST FRAMEWORK (DRF)
# Autenticación JWT, Filtros y Documentación OpenAPI
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ==============================================================================
# CONFIGURACIÓN SIMPLE JWT (AUTENTICACIÓN CON CLAIMS DE ROL)
# ==============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ==============================================================================
# DOCUMENTACIÓN OPENAPI / SWAGGER (DRF-SPECTACULAR)
# Accesible de manera interactiva en /api/docs/
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Arriendo de Maquinaria de Construcción (Renting / Servicios)',
    'DESCRIPTION': (
        'Plataforma integral de gestión y arriendo de maquinarias pesadas y equipos industriales. '
        'Incluye autenticación JWT con control de acceso basado en roles (RBAC: Empresa Constructora '
        'y Ejecutivo de Arriendos), carro persistente en PostgreSQL, transacciones atómicas para control '
        'de flota y cálculo de tarifas.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True
