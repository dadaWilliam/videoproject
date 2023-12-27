import mimetypes
import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'test'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'sorl.thumbnail',
    'chunked_upload',
    'video',
    'users',
    'myadmin',
    'comment',
    'history',
    'rest_framework',
    'user_visit',
    'notice',
    'notifications',
    "django_top_notify",
    'django_tctip',
    'django_filters',
    'qrcode',
    'ckeditor',
    'article',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.ippass.XForwardedForMiddleware',
    'video.middleware.loginrequired.LoginRequiredMiddleware',
    'user_visit.middleware.UserVisitMiddleware',
    'video.middleware.blockinvalidvideo.BlockInvalidVideoMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

SITE_URL = 'xueba.ca'

ROOT_URLCONF = 'videoproject.urls'

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = '/users/login/'
# OPEN_URLS = ['/users/signup/']
OPEN_URLS = ['/article/', '/file/', '/users/feedback/', '/myadmin/', '/ad/']
REPAIR_URL = '/maintenance/'

LOGIN_REDIRECT_URL = '/video/index'

THUMBNAIL_DEBUG = True

# 文件上传路径
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload').replace('\\', '/')
MEDIA_URL = '/upload/'

# 上传视频最大尺寸
CHUNKED_UPLOAD_MAX_BYTES = 100000000

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# 邮件配置
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'net936@163.com'
EMAIL_HOST_PASSWORD = 'your pwd'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'videoproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # {
    #    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

# Define the supported languages
LANGUAGES = [
    ('zh-hans', 'Simplified Chinese'),
    ('en-gb', 'English (UK)'),  # UK English
    ('en-us', 'English (US)'),  # US English
    ('zh-hant', 'Traditional Chinese'),
]

# Set path to store translation files
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


STATIC_URL = '/static/'


# collect_static path, must be static
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# 设置图片等静态文件的路径
STATICFILES_DIRS = (
    ('css', os.path.join(STATIC_ROOT, 'css').replace('\\', '/')),
    ('js', os.path.join(STATIC_ROOT, 'js').replace('\\', '/')),
    ('img', os.path.join(STATIC_ROOT, 'img').replace('\\', '/')),
)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 86400

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 自定义认证类路径
        'video.authentication.CustomAuthentication',

    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/min',
        'user': '200/minute',
    },
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(days=10),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=11),
# }
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
