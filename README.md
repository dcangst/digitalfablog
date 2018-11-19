# DigitalFablog

This is a very much work in progress application to manage FabLab Zürich

## Development

### Setup

1. setup a python3 environment to run django in (outside of repository) and activate it and switch into the digitalfablog repository

```
virtualenv -p python3 py-env
source py-env/bin/activate; cd digitalFablog;
```

2. install dependencies
```
pip install -r requirements.txt
```

3. generate .env file from example.env, i.e. copy and change relevant settings (uses python-decouple as described [here](https://simpleisbetterthancomplex.com/series/2017/10/16/a-complete-beginners-guide-to-django-part-7.html))

4. initialize database

```
python manage.py sqlcreate | psql -U <db_administrator> -W
```

5. initialize django models

```
python manage.py makemigrations
python manage.py migrate
```

6. create django superuser e.g. like this:

```
echo "from members.models import User; User.objects.create_superuser(email='bruce@wayneindustries.com', first_name='Bruce', last_name='Wayne', street_and_number='Wayne manor', zip_code='1234', city='Gotham', phone = '098934973982', birthday='1939-2-19', password='iamthebatman')" | python manage.py shell
```

7. (somewhat optional) load initial data from fixtures

```
python manage.py loaddata initial_cashier initial_machines initial_authgroups initial_memberships
```

### Code Style

I use flake8 with linelenght set to 120 (since no one is going to print this)
