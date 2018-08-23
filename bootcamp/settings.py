# coding:utf-8

import os
from django.utils.translation import ugettext_lazy as _


SECRET_KEY = '8n2r(b-l1+jqats9k@)5dr=w3qe(0c$!wc*=z2jik4ivx_y0yu'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

# 通过这个开关来判断是否load 开发配置文件／生产环境配置文件
if DEBUG:
    # 测试用的配置
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# project 的目录：在bootcamp包内
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# http://python.usyiyi.cn/django/ref/settings.html#allowed-hosts
# 一般设置全部允许
ALLOWED_HOSTS = ['*']

# Application definition

# 这里注意， 因为所有app都在bootcamp中，所以包名有所变化
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'bootcamp.activities',
    'bootcamp.articles',
    'bootcamp.authentication',
    'bootcamp.core',
    'bootcamp.feeds',
    'bootcamp.messenger',
    'bootcamp.questions',
    'bootcamp.search',
)

# 设置中间件

#  LocaleMiddleware ： 国际化的中间件

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# 定义url的入口配置
ROOT_URLCONF = 'bootcamp.urls'

# 定义wsgi应用的入口配置
WSGI_APPLICATION = 'bootcamp.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# 设置网站的默认语言
LANGUAGE_CODE = 'en-us'

# 默认时区, 存成标准时区UTC，有助于多时区翻译
TIME_ZONE = 'UTC'

# 18N : 翻译
# 10N : 格式化日期
USE_I18N = True
USE_L10N = True

# 设置时区，设置时区之后，会自动的翻译时区的
# 默认是False
# True：内部使用datetime-with-tz
# False：使用的都是local datetime
USE_TZ = True

# 注意中文支持语言的写法
LANGUAGES = (
    ('en', _('English')),
    ('pt-br', _('Portuguese')),
    ('es', _('Spanish')),
    # ('zh-cn', _('Chinese')),
)

# 标注本地化翻译语言的位置
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# collectstatic用于部署而收集的静态文件的目录的绝对路径。
# collectstatic 管理命令将收集的静态文件到这个目录
STATIC_ROOT = os.path.join(os.path.dirname(PROJECT_DIR), 'staticfiles')

# 静态文件的url
# http://xxxxx/static/xxxx.png
# 注意！！！！
# production环境(debug=False)：Django不会再提供静态文件接续
# 需要web server去处理
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
)

# 指向存放用户上传文件所在目录的文件系统绝对路径。
MEDIA_ROOT = os.path.join(os.path.dirname(PROJECT_DIR), 'media')

# 通过这个地址来管理所存储文件。
# 最好用nginx等web server访问静态文件
MEDIA_URL = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')]
        ,
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

# 登录的URL，特别是使用login_required() 装饰器的时候。
LOGIN_URL = '/'

# 登录之后，contrib.auth.login 视图找不到next 参数时，请求被重定向到的URL。
LOGIN_REDIRECT_URL = '/feeds/'

ALLOWED_SIGNUP_DOMAINS = ['*']

# 文件上传的临时目录
FILE_UPLOAD_TEMP_DIR = '/tmp/'
FILE_UPLOAD_PERMISSIONS = 0644
