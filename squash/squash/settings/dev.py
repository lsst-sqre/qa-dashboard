# Specific settings for development

from .defaults import *

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Needed by django debug toolbar
INTERNAL_IPS='127.0.0.1'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME' : 'qadb',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
              'charset': 'utf8mb4',
              'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1",
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    }


}

BOKEH_URL='http://localhost:5006'
