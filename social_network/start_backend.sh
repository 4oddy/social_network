# apply migrations
python "./manage.py" migrate

# collect static into dir
python "./manage.py" collectstatic

# start server
exec gunicorn -c "./gunicorn_config_docker.py" first_site.wsgi