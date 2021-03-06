import json
import os

import dj_database_url
from cfenv import AppEnv

from .base import *  # noqa

env = AppEnv()

DEBUG = False
ANALYTICS = {
    'DAP': {
        'AGENCY': 'GSA'
    }
}

DATABASES = {
    'default': dj_database_url.config()
}


vcap_app = json.loads(os.environ.get('VCAP_APPLICATION', '{}'))
ALLOWED_HOSTS = ['localhost'] + vcap_app.get('application_uris', [])

vcap_services = json.loads(os.environ.get('VCAP_SERVICES', '{}'))
es_config = vcap_services.get('elasticsearch-swarm-1.7.1', [])
if es_config:
    HAYSTACK_CONNECTIONS['default'] = {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': es_config[0]['credentials']['uri'],
        'INDEX_NAME': 'eregs',
    }

redis = env.get_service(label='redis28-swarm')
if redis:
    # safe because: the password str is telling get_url what key to use when
    # looking up a value
    url = redis.get_url(    # nosec
        host='hostname', password='password', port='port')
    BROKER_URL = 'redis://{}'.format(url)
    CACHES['regs_gov_cache']['LOCATION'] = BROKER_URL
    CACHES['regs_gov_cache']['BACKEND'] = 'django_redis.cache.RedisCache'


s3 = env.get_service(label='s3')
if s3:
    ATTACHMENT_ACCESS_KEY_ID = s3.credentials.get('access_key_id')
    ATTACHMENT_SECRET_ACCESS_KEY = s3.credentials.get('secret_access_key')
    ATTACHMENT_BUCKET = s3.credentials.get('bucket')

REGS_GOV_API_URL = env.get_credential(
    'REGS_GOV_API_URL', os.environ.get('REGS_GOV_API_URL'))
REGS_GOV_API_LOOKUP_URL = env.get_credential(
    'REGS_GOV_API_LOOKUP_URL', os.environ.get('REGS_GOV_API_LOOKUP_URL'))
REGS_GOV_API_KEY = env.get_credential(
    'REGS_GOV_API_KEY', os.environ.get('REGS_GOV_API_KEY'))
HTTP_AUTH_USER = env.get_credential('HTTP_AUTH_USER')
HTTP_AUTH_PASSWORD = env.get_credential('HTTP_AUTH_PASSWORD')

# HTTP Auth may have be different due to the above lines
if HTTP_AUTH_USER and HTTP_AUTH_PASSWORD:
    API_BASE = 'http://{}:{}@localhost:{}/api/'.format(
        HTTP_AUTH_USER, HTTP_AUTH_PASSWORD,
        os.environ.get('VCAP_APP_PORT', '8000'))

# Cookie settings - we don't inspect the contents of cookies, but this is good
# practice
SESSION_COOKIE_HTTPONLY = True  # note that this is also Django's default
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
