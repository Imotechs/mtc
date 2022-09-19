
from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=)i#h+%h$o*1c6ob7pbcvfka@q^1e=o=&rni**wjb!$270bhoy'

handler404 = 'mainapp.views.page_not_found_view'
handler500 = 'mainapp.views.my_custom_error_view'
handler403 = 'mainapp.views.page_restricted_view'


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LOGIN_REDIRECT_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/


STATIC_URL = 'static/'

MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend','mainapp.backend.EmailAuthBackend']

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'#'django.core.mail.backends.console.EmailBackend'#'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'stakegams@gmail.com'
EMAIL_HOST_PASSWORD = 'vzhdmyybysgtcgih'

PAYSTACK_SECRET_KEYS  = 'sk_live_f18eef317caaf562616360a056f83e5946caa27f'
PAYSTACK_PUBLICK_KEYS = 'pk_live_058f02e321c817c82da1aa67dc53c29109b20910'
