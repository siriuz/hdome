"""
Django settings for hdome project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_0-zw7xmw*(u8te_)ccg&5lq%7&j!4k7bt6&=@)@#0rsz_r!8w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]


ALLOWED_HOSTS = []

LOGIN_URL = '/login'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pepsite',
    'django_extensions',
    'guardian',
    'news',
    "djcelery_email",
    #'debug_toolbar.apps.DebugToolbarConfig',
    'djcelery',
    #'south',
    
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # default
    'guardian.backends.ObjectPermissionBackend',
)


FIXTURE_DIRS = (
   '/home/rimmer/praccie/hdome/pepsite/fixtures/',
)

ANONYMOUS_USER_ID = -1

ROOT_URLCONF = 'hdome.urls'

WSGI_APPLICATION = 'hdome.wsgi.application'


# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

#CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
#CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend'
#BROKER_URL = 'redis://localhost:6379/0'
#BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}  # 1 hour - same as default
#CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hdometwo',
	'HOST' : '',
	'USER': 'rimmer',
        'PASSWORD': 'f',
        # 'HOST': '127.0.0.1', # if we wanna use TCP sockets
        # 'PORT': '5432', # if we wanna use TCP sockets
    }
}


#EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'kieranrimmer'
EMAIL_HOST_PASSWORD = 'kingysback'
EMAIL_USE_TLS = True


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join( BASE_DIR, 'static_root' )

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    #'/var/www/static/',
)

SHELL_PLUS_PRE_IMPORTS = (
    'pprint',
    'uniprot',
    ( 'db_ops.dbtools', 'DBTools' ),    
    ( 'pepsite.make_searches', '*' ),    
    ( 'pepsite.tasks', '*' ),
    ( 'guardian.shortcuts', 'assign_perm' ),
    ( 'django.db', 'connection' ),
    #('module.submodule1', ('class1', 'function2')),
    #('module.submodule2', 'function3'),
    #('module.submodule3', '*'),
    #'module.submodule4'
    )

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
