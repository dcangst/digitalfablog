# DigitalFablog

This is a very much work in progress application to manage FabLab Zürich

## Development

1. setup a python3 environment to run django in (outside of repository) and activate it and switch into the digitalfablog repository

```
virtualenv -p python3 py-env
source py-env/bin/activate; cd digitalFablog;
```

2. install dependencies
```
pip install -r requirements.txt
```

3. initialize database

```
python manage.py sqlcreate | psql -U <db_administrator> -W
```

4. initialize django models

```
python manage.py makemigrations
python manage.py migrate


```
5. create django superuser e.g. like this:
```
echo "from members.models import User; User.objects.create_superuser(email='bruce@wayneindustries.com', first_name='Bruce', last_name='Wayne', street_and_number='Wayne manor', zip_code='1234', city='Gotham', phone = '098934973982', birthday='1939-2-19', password='iamthebatman')" | python manage.py shell
```

