# My Life Rest API

## Configuration

### 1. On API Project:

For development and testing, We recommend using the [PyCharm IDE](https://www.jetbrains.com/pycharm/).

If you don't have pip installed, execute the following commands (on Ubuntu):

```bash
sudo apt install python-pip
sudo apt install python3-pip
```

If you don't have pipenv installed, execute the following commands:

```bash
sudo -H pip install -U pipenv
sudo -H pip3 install -U pipenv
```

Before starting the project, first check if the pipenv environment is default and is configured on the PyCharm IDE. For that, follow these steps:

Firstly open the settings, executing the keyboard shortcut CTRL+ALT+S or through the menu File and then Settings. Your settings should be like this:

![settings](https://i.imgur.com/DF3OZkp.png)

If the project interpreter isn't Pipenv, then click on the settings wheel on the right and click Add..., and after this click on the Pipenv Environment menu, and the result should be like this:

![pipenv](https://i.imgur.com/5Z75ohQ.png)

If all went well, the Pipenv executable has a path to the system pipenv directory, and all you need to do is press OK. Finally, press OK to confirm the Pipenv Environment, and it should all be set.
To start the project, just do the next step (2. MySQL Database), and if a message shows up, on the PyCharm IDE, to install the requirements, just accept it.

| Action                                                  | Command                                                                                                                                                                          |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Get inside of the venv directory                        | `pipenv shell`                                                                                                                                                                   |
| Dependencies Installed (No need to install them again!) | `pipenv install "djangorestframework>=3.10.3"` ; `pipenv install django-rest-swagger` ; `pipenv install requests` ; `pipenv install "django>=3.0.3"` ; `pipenv install psycopg2` |

### 2. PostgreSQL Database

On Ubuntu:

| Action                                      | Command                                                                                    |
| ------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Install PostgreSQL                               | `apt-get install postgresql postgresql-contribr` ; `apt-get install libpq-dev python3-dev` |
| Access PostgreSQL as admin                       | `sudo -u postgres -i`                                                                      |
| Login in PostgreSQL Database                  | `psql`                                                                                     |
| Create a new user and set it's password     | `CREATE USER 'mylife' WITH PASSWORD 'mylife-restapi-2020';`                                |
| Create the database                         | `CREATE DATABASE mylife WITH OWNER mylife;`                                                |
| Grant priviliges to the new user            | `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mylife;`                           |
| Find out the port where PostgreSQL is running | `SELECT setting AS port FROM pg_settings WHERE name = 'port';`                             |

After this steps, we will need to configure our REST API to access the new database we just created. For doing so, in `settings.py`file of the REST API Django Project we need to add the following code:

```python
# Connect to external database
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': '<db_name>',                        # mylife
            'USER': "<user_name>",                      # mylife
            'PASSWORD': "<pw_for_user>",                # mylife-restapi-2020
            'HOST': "<host>",                           # localhost
            'PORT': "<db_port>",                        # 5432
        }
    }
```

Now, we have connected our REST API to our database. The only thing that's missing is to create the tables that will have the information we need. To create this tables, on the REST API Django Project we need to execute the following commands:

**First, we have to delete the migrations folder, if it exists.**

**Then, execute the following commands:** (The <app_name> is the name of the folder that contains the models.py file.)

```bash

python3 manage.py check
python3 manage.py makemigrations <app_name>
python3 manage.py sqlmigrate <app_name> 0001
python3 manage.py migrate <app_name>
```

It is advised to create a Django Admin that can be accessed on a browser, trough `<host>:<port>/admin`.
For this, execute the following command:

```bash
python3 manage.py createsuperuser
```

Ex:

- Username: _admin_
- Email: _admin@admin.com_
- Password: _admin_

To access the database from command line, execute the following:
```bash
psql -U mylife -h 127.0.0.1 mylife
```

<!--We are almost ready to deploy this REST API, we are only missing a minor detail. We should configure in which port this API will be accessible.
To do this, in `manage.py` we need to add the following lines:

```python
from django.core.management.commands.runserver import Command as runserver
runserver.default_port = "<port>"   #9000
```-->
