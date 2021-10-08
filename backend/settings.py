"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g)kql6&a66vmui3mhcoq4!1p1m8nna#rbrdnr+pc0ij$vvht!#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'admin_shortcuts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # 3rd party lib
    # *** Registration endpoint
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',

    'corsheaders',  # Changed line (46->41), Allow/Add CORS to Request/Response
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth', # for logIn, LogOut 
    'djoser',
    'mptt',
    'ckeditor',
    'colorfield',
    'multiselectfield',

    # local
    'aptusadmin',
    'e_commerce',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            (os.path.join(BASE_DIR, 'templates')),
        ],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE':
    100
}

AUTH_USER_MODEL = 'aptusadmin.CustomUser'

DJOSER = {
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SET_PASSWORD_RETYPE": True,
    'ACTIVATION_URL': 'aptusadmin/activate/{uid}/{token}/',
    'SEND_ACTIVATION_EMAIL': True,
    'PASSWORD_RESET_CONFIRM_URL': 'aptusadmin/password_reset/{uid}/{token}/',
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
}

#  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # for gmail
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # new
EMAIL_HOST_USER = ''  # in order to aptusadmin email verification to work
EMAIL_HOST_PASSWORD = ''  # in order to aptusadmin email verification to work
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

FRONT_END = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

#  CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
] + FRONT_END
# from corsheaders.defaults import default_methods
# from corsheaders.defaults import default_headers
# to keep up to date with any future changes
#
# CORS_ALLOW_METHODS = list(default_methods) + [
#  "POKE",
#  ]
#
#  CORS_ALLOW_HEADERS = list(default_headers) + [
#  "my-custom-header",
#  ]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


if not DEBUG:
    STATICFILES_DIRS = [
        os.path.join(STATIC_ROOT, 'css/'),
        os.path.join(STATIC_ROOT, 'js/'),
        os.path.join(STATIC_ROOT, 'img/')
    ]

# TODO: Create 3 diff settings for (dev, prod, 3rd-party librairies)
# 3rd-party configuation

BACKEND_URL = "http://localhost:8000"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_SHORTCUTS = [
    {
        'title':
        'E-commerce',
        'shortcuts': [
            {
                'title': 'Ajouter un Produit',
                'url_name': 'admin:e_commerce_produit_add',
                'icon': 'plus',
            },
            {
                'title': 'Liste des Produits',
                'url_name': 'admin:e_commerce_produit_changelist',
                'icon': 'box',
                'count': 'e_commerce.views.nb_produits',
            },
            {
                'title': 'Liste des Categories',
                'url_name': 'admin:e_commerce_categorie_changelist',
                'icon': 'align-left',
                'count': 'e_commerce.views.nb_categories',
            },
            {
                'title': 'Liste des Clients',
                'icon': 'user',
                'url_name': 'admin:e_commerce_client_changelist',
                'count': 'e_commerce.views.nb_clients',
            },
            {
                'title': 'Liste des Commandes',
                'url_name': 'admin:e_commerce_commande_changelist',
                'icon': 'shopping-bag',
                'count': 'e_commerce.views.nb_commandes',
            },
            {
                'title': 'Liste des Paniers des clients',
                'url_name': 'admin:e_commerce_panier_changelist',
                'icon': 'shopping-cart',
                'count': 'e_commerce.views.nb_paniers',
            },
            {
                'title': 'Notes de recommandation',
                'url_name': 'admin:e_commerce_notederecommandation_changelist',
                'icon': 'star',
                'count': 'e_commerce.views.nb_notes',
            },
            {
                'title': 'Messages de contact',
                'url_name': 'admin:e_commerce_contact_changelist',
                'icon': 'envelope',
                'count': 'e_commerce.views.nb_messages',
            },
            {
                'title': 'Paramètres du site',
                'url': '/admin/e_commerce/sitesettings/1/change/',
                'icon': 'cog',
            },
        ]
    },
]
ADMIN_SHORTCUTS_SETTINGS = {
    'show_on_all_pages': True,
    'hide_app_list': False,
    'open_new_window': False,
}
