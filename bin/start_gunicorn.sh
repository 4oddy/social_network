source /home/roddy/Desktop/social_network/venv/local/bin/activate
exec gunicorn -c "/home/roddy/Desktop/social_network/social_network/gunicorn_config.py" first_site.wsgi
