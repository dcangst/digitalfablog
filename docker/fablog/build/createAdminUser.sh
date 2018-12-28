#!/bin/bash

echo "from members.models import User; User.objects.create_superuser(email='bruce@wayneindustries.com', first_name='Bruce', last_name='Wayne', street_and_number='Wayne manor', zip_code='1234', city='Gotham', phone = '098934973982', birthday='1939-2-19', password='iamthebatman')" | python manage.py shell
