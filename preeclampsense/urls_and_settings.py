# backend/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('sync/bp/',            views.sync_bp,        name='sync-bp'),
    path('sync/urine/',         views.sync_urine,     name='sync-urine'),
    path('alerts/',             views.create_alert,   name='create-alert'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve-alert'),
    path('dashboard/',          views.dashboard_stats, name='dashboard'),
]

# ─────────────────────────────────────────────────────────────────────────────
# backend/preeclampsense/settings.py  (Render-ready)
# ─────────────────────────────────────────────────────────────────────────────
"""
Django settings for PreeclampSense backend.
Configured for Render.com free tier deployment.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-change-this-in-production-abc123'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    '*',   # tighten in production
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'preeclampsense',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'preeclampsense.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

# Database — SQLite locally, PostgreSQL on Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   BASE_DIR / 'db.sqlite3',
    }}

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

CORS_ALLOW_ALL_ORIGINS = True   # tighten in production

# ─────────────────────────────────────────────────────────────────────────────
# backend/preeclampsense/urls.py
# ─────────────────────────────────────────────────────────────────────────────
"""
ROOT_URLCONF urls.
"""
from django.contrib import admin
from django.urls    import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',   include('api.urls')),
]
