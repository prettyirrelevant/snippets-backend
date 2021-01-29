import environ

from .development import *

env = environ.Env(DEBUG=(bool, False))

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

SECRET_KEY = env('SECRET_KEY')

DATABASES = {'default': env.db()}

CORS_ALLOWED_ORIGINS = ['https://snippets-app.vercel.app']
