# social_network

This is my very big project written on django4 

# how to start

First of all, you have to make virtual env by this command

`python -m venv venv`

Then, install dependencies 

`pip install -r requirements.txt`

Go into dir social_network

`cd social_network`

And run testing server

`python manage.py runserver`

It's not all. If SEND_EMAILS in first_site/setting.py is True, you have to run celery worker and rabbitmq docker container
