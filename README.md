# social_network

This is my very big project written on django4 

# how to start

First of all, you have to make virtual env by this command

`python -m venv venv`

Then, install dependencies 

`pip install -r requirements.txt`

Set .env settings for secret key and database

Go into dir social_network

`cd social_network`

Make migrations

`python manage.py makemigrations`

Apply them

`python manage.py migrate`

And run testing server

`python manage.py runserver`

It's not all. If SEND_EMAILS in first_site/setting.py is True, you have to run celery worker and rabbitmq docker container

`celery -A first_site worker -P eventlet --loglevel info`

This will start a celery worker. To enter this command, you have to be in social_network dir

`docker run -d --hostname my-rabbit --name some-rabbit rabbitmq:3`

This will start a RabbitMQ container listening on the default port of 5672.
