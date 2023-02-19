command = '/home/roddy/.local/bin/gunicorn'
pythonpath = '/home/roddy/Desktop/social_network/social_network'
bind = '127.0.0.1:8002'
workers = 5
user = 'roddy'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=first_site.settings'
