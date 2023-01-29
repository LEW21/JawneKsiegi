DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = (
	'django.contrib.staticfiles',
	'kw',
	'debug_toolbar',
)

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
	'django.middleware.common.CommonMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',
]

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
			],
		},
	},
]

STATIC_ROOT = 'static'
STATIC_URL = 'static/'

ROOT_URLCONF = 'jawneksiegi.urls'
WSGI_APPLICATION = 'jawneksiegi.wsgi.application'

from dj12.config import *

if DEBUG:
	INTERNAL_IPS = ['127.0.0.1']
