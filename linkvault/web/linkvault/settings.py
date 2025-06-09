import environ, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

env = environ.Env()
env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

# DEBUG = False

# ALLOWED_HOSTS = ['localhost']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party
    'django_email_verification',
    'social_django',
    # my apps
    'accounts.apps.AccountsConfig',
    'links.apps.LinksConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'linkvault.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'links.context_processors.show_exit_warning',
            ],
        },
    },
]

WSGI_APPLICATION = 'linkvault.wsgi.application'



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': env('POSTGRES_DB'),
#         'USER': env('POSTGRES_USER'),
#         'PASSWORD': env('POSTGRES_PASSWORD'),
#         'HOST': env('POSTGRES_HOST'),
#         'PORT': env('POSTGRES_PORT', default=5432),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameBackend',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'accounts.CustomUser'


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


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'  

STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_DIRS = [
    BASE_DIR / 'linkvault' / 'static'
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


''' Sessions '''
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1209600  


""" LOGGER """
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { # Формат самих логов
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO', # Указание уровня логирования для записи в файл
            'class': 'logging.FileHandler',
            'filename': 'logs/linkvault.log', # Путь к файлу для сохранения логов
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'accounts': {  # пустая строка = корневой логгер (всё приложение)
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'links': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': { # Название приложения для логирования
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


""" Django Email Verification """

def email_verified_callback(user):
    user.is_active = True


def password_change_callback(user, password):
    user.set_password(password)


# Global Package Settings
EMAIL_FROM_ADDRESS = 'noreply@aliasaddress.com'  # mandatory
EMAIL_PAGE_DOMAIN = 'http://127.0.0.1:8000/'  # mandatory (unless you use a custom link)
EMAIL_MULTI_USER = False  # optional (defaults to False)

# Email Verification Settings (mandatory for email sending)
EMAIL_MAIL_SUBJECT = 'Подтверди свой email {{ user.username }}'
EMAIL_MAIL_HTML = 'accounts/email/mail_body.html'
EMAIL_MAIL_PLAIN = 'accounts/email/mail_body.txt'
EMAIL_MAIL_TOKEN_LIFE = 60 * 60  # one hour

# Email Verification Settings (mandatory for builtin view)
EMAIL_MAIL_PAGE_TEMPLATE = 'accounts/email/email_success_template.html'
EMAIL_MAIL_CALLBACK = email_verified_callback

# Password Recovery Settings (mandatory for email sending)
EMAIL_PASSWORD_SUBJECT = 'Измени свой пароль {{ user.username }}'
EMAIL_PASSWORD_HTML = 'accounts/password/password_body.html'
EMAIL_PASSWORD_PLAIN = 'accounts/password/password_body.txt'
EMAIL_PASSWORD_TOKEN_LIFE = 60 * 10  # 10 minutes

# # Password Recovery Settings (mandatory for builtin view)
EMAIL_PASSWORD_PAGE_TEMPLATE = 'accounts/password/password_changed_template.html'
EMAIL_PASSWORD_CHANGE_PAGE_TEMPLATE = 'accounts/password/password_change_template.html'
EMAIL_PASSWORD_CALLBACK = password_change_callback

# For Django Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'kadyevsultan521@gmail.com'
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True



""" Social Auth """
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

LOGIN_URL = '/auth/login/google-oauth2/'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SOCIAL_AUTH_URL_NAMESPACE = 'social'

# Для связки аккаунта Google с аккаунтом в LinkVault
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',  # <- привязка
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
