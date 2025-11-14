import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url
import cloudinary

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
MODE = os.getenv('MODE', 'DEVELOPMENT')

DEBUG = os.getenv('DEBUG', 'False')

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'authentication.User'

INSTALLED_APPS = [
    "jazzmin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'core.authentication',
    'core.goroutes',
    'core',
    'core.uploader',
    'django_extensions',
    'django_filters',
    'channels',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    # "DEFAULT_AUTHENTICATION_CLASSES": ("core.authentication.TokenAuthentication",),
    # "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",),
#     'DEFAULT_PAGINATION_CLASS': 'config.pagination.CustomPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
#     'PAGE_SIZE': 10,
 'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

WSGI_APPLICATION = 'config.wsgi.application'

if MODE == 'DEVELOPMENT':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3',
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'x-requested-with',
    'accept',
    'origin',
    'x-csrftoken',
]

CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']

SPECTACULAR_SETTINGS = {
    'TITLE': 'GoRoutes API',
    'DESCRIPTION': 'API for manage GoRoutes, including endpoints and documentation.',
    'VERSION': '1.0.0',
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "core/static",
]

ALLOWED_HOSTS = ['*']

CLOUD_NAME = os.getenv('CLOUD_NAME')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_URL'))],
        },
    },
}

JAZZMIN_SETTINGS = {
    "site_title": "GoRoutesAdmin",
    "site_header": "GoRoutes",
    "site_brand": "GoRoutesAdmin",
    "welcome_sign": "Bem-vindo ao painel do GoRoutes",
    "copyright": "GoRoutes © 2025",
    "site_logo": "img/logoRemovedWhite.png",  # relativo à pasta static

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "authentication.driver": "fa fa-id-card",
        "authentication.address": "fa fa-map-marker",
        "authentication.passenger": "fa fa-bus",
        "authentication.responsible": "fa fa-user-shield",
        "authentication.user": "fa fa-user",
        "authentication.studentdata": "fa fa-graduation-cap",
        "goroutes.route": "fa fa-road",
        "goroutes.vehicle": "fa fa-shuttle-van",
        "uploader.image": "fa fa-image",
        "uploader.document": "fa fa-file",
        "goroutes.dailyroute": "fa fa-calendar-day",
    },

    "order_with_respect_to": ["core.authentication", "core.goroutes", "core.uploader"],

    "custom_links": { },
}

JAZZMIN_UI_TWEAKS = {
    # ---------- Tema geral ----------
    "theme": "cyborg",  # Tema Bootswatch aplicado ao admin. Ex: 'lux', 'darkly', 'cyborg', 'flatly', etc.
    "dark_mode_theme": "darkly",  # Tema usado quando dark mode é ativado

    # ---------- Navbar ----------
    "navbar": "navbar-dark bg-primary",  # Classes CSS aplicadas à navbar
    "no_navbar_border": False,           # Remove a borda inferior da navbar se True
    "navbar_fixed": True,                # Fixa a navbar no topo da página

    # ---------- Sidebar ----------
    "sidebar": "sidebar-dark-primary",   # Classes CSS aplicadas à sidebar
    "sidebar_nav_small_text": True,      # Usa texto menor nos itens do menu
    "sidebar_disable_expand": False,     # Impede expansão automática do menu de sidebar
    "sidebar_nav_child_indent": True,    # Indenta os menus filhos
    "sidebar_nav_compact_style": True,   # Reduz padding dos itens da sidebar
    "sidebar_fixed": True,               # Sidebar fixa durante scroll

    # ---------- Footer ----------
    "footer_fixed": True,               # Fixa o footer no final da tela

    # ---------- Body ----------
    "body_small_text": False,             # Torna todo o texto do corpo menor
    "brand_colour": "navbar-primary",       # Cor da marca exibida no topo
    "accent": "accent-primary",          # Cor de destaque usada em badges, links, etc.

    # ---------- Botões ----------
    "button_classes": {
        "primary": "btn btn-primary",       # Classe do botão primário
        "secondary": "btn btn-secondary",   # Classe do botão secundário
        "info": "btn btn-info",             # Classe do botão de informação
        "warning": "btn btn-warning",       # Classe do botão de aviso
        "danger": "btn btn-danger",         # Classe do botão de perigo
        "success": "btn btn-success",       # Classe do botão de sucesso
    },

    # ---------- Formulários ----------
    "form_label_top": True,               # Coloca labels acima dos inputs
    "form_small_text": True,              # Inputs com texto menor
    "form_control_border": True,          # Adiciona borda nos inputs

    # ---------- Listagens (Change List) ----------
    "list_filter_small_text": True,       # Texto menor nos filtros laterais
    "list_select_related": True,          # Usa select_related para otimizar queries
    "list_display_links": True,           # Torna colunas clicáveis na lista

    # ---------- Modais ----------
    "modal_size": "modal-lg",             # Tamanho padrão dos modais (ex: 'modal-sm', 'modal-lg', 'modal-xl')

    # ---------- Branding ----------
    "brand_logo": None,                   # Caminho do logo customizado
    "brand_logo_classes": "img img-fluid",  # Classes CSS aplicadas ao logo
    "brand_logo_width": 50,               # Largura do logo
}

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'rpc://'  # Ou use 'redis://...' se preferir

SHELL_PLUS = "ipython"

# Arquivo de pre-imports para o shell
SHELL_PLUS_PRE_IMPORTS = [
    ('core.goroutes.tasks', ('clear_cache_table', 'make_cache_distance_passengers', 'geocode_all_addresses')),
]
