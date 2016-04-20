# Specific settings for development

from . import defaults

DEBUG = defaults.os.environ.get('DEBUG', 'True') == 'True'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': defaults.os.path.join(defaults.BASE_DIR, 'db.sqlite3'),
    }
}
