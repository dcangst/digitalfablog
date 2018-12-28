#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_cashier initial_machines initial_materials initial_authgroups initial_memberships
python manage.py runserver 0.0.0.0:80
