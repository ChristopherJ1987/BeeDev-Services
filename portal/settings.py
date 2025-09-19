import os
from environ import Env

env = Env(
    DEBUG=(bool, False)
)
env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='dev-server-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# -------- Hosts & CSRF (add your domains) --------
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    'localhost', '127.0.0.1',
    'portal.beedev-services.com',
])
CSRF_TRUSTED_ORIGINS = [
    'https://beedev-services.com',
    'https://www.beedev-services.com',
    'https://portal.beedev-services.com',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'userApp.apps.UserappConfig',
    'companyApp.apps.CompanyappConfig',
    'proposalApp.apps.ProposalappConfig',
    'invoiceApp.apps.InvoiceappConfig',
    'projectApp.apps.ProjectappConfig',
    'ticketApp.apps.TicketappConfig',
    'prospectApp.apps.ProspectappConfig',
    'core.apps.CoreConfig',
    # Only load browser reload in dev (optional but recommended)
    *(['django_browser_reload'] if env.bool('DEBUG', default=False) else []),
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # only in dev
    *( ['django_browser_reload.middleware.BrowserReloadMiddleware'] if env.bool('DEBUG', default=False) else [] ),
]

ROOT_URLCONF = 'portal.urls'

# -------- Templates: allow project-level overrides (admin/login.html etc.) --------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'core.context_processors.beedev_defaults',
            ],
        },
    },
]

WSGI_APPLICATION = 'portal.wsgi.application'


# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        # 'ENGINE': 'mysql.connector.django',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validation
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


# -------- Auth: shared login + redirects --------
AUTH_USER_MODEL = 'userApp.User'
LOGIN_URL = 'userApp:login'
LOGIN_REDIRECT_URL = 'userApp:post_login'
# LOGOUT_REDIRECT_URL = 'https://beedev-services.com/'
LOGOUT_REDIRECT_URL = '/'
PROSPECTS_CLIENT_MODEL = "companyApp.Company"
# Base URL of your future signing page (view will look up Proposal by token)
# PROPOSAL_SIGNING_URL_BASE = "https://portal.example.com/sign"
# Dotted-callables (set now or later)
PROPOSAL_ACCOUNT_CREATOR = "proposalApp.hooks:create_account_for_signed_proposal"
PROPOSAL_INVOICE_CREATOR = "proposalApp.hooks:create_invoice_for_deposit"
PROPOSAL_MESSENGER       = "proposalApp.hooks:send_proposal_email"


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Eastern'
USE_I18N = True
USE_TZ = True

# -------- Static files: separate source vs. collect dir --------
# Use /static/ as URL (leading and trailing slash)
STATIC_URL = '/static/'

# Project-level source folder for your brand CSS/logo (used in dev; collected in prod)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Final collect destination for production (run `collectstatic` -> served by web server/WhiteNoise)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media (unchanged)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------- Production hardening (safe to set; they no-op in dev) --------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
