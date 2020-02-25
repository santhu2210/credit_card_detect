#!/bin/bash
# works only when run from server directory as the current working directory
export DJANGO_DEBUG=true
#python setup_server.py
python manage.py runserver 0.0.0.0:8000
