import environ

from .development import *

env = environ.Env(DEBUG=(bool, False))

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

SECRET_KEY = env('SECRET_KEY')

DATABASES = {'default': env.db()}

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
