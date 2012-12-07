# Django settings for jdata project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_PATH = os.path.split(os.path.abspath(__file__))[0]
PROJECT_DIR = PROJECT_PATH
PROJECT_NAME = PROJECT_PATH.strip().strip('/').split('/')[-1]

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

#PROJECT_DIR = '/data/svn/sysnetrd/trunk/jdata/'
PROJECT_DIR = os.getcwd()

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'jdata',                      # Or path to database file if using sqlite3.
        'USER': 'jdata',                      # Not used with sqlite3.
        'PASSWORD': 'jdata',                  # Not used with sqlite3.
        'HOST': 'bjcnc.jdata.w.qiyi.db',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '6069',                      # Set to empty string for default. Not used with sqlite3.
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

LOGFILE = os.path.join(PROJECT_DIR,PROJECT_NAME+'.log')
# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/static/"
STATICFILES_ROOT = ''

# URL that handles the static files served from STATICFILES_ROOT.
# Example: "http://static.lawrence.com/", "http://example.com/static/"
STATICFILES_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# A list of locations of additional static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    #'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gwh(#gw9i_=6a#a+l+2k-psq0=(d_c6bp#vguh$@hn@)^=tkd5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR,'templates'),
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djutils.middleware.JdataMiddleware',
)

ROOT_URLCONF = 'jdata.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    #'django.contrib.staticfiles',
    # 'django.contrib.admindocs',
     'django.contrib.admin',
     'app',
)


CACHE_BACKEND = "memcached://10.11.50.44:11211/?timeout=3600"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_URI = '/login/'
LOGOUT_URI = '/logout/'
REGISTION_URI = '/registion/'
SQLURI = "mysql://user:password@host:port/database?charset=utf8"
