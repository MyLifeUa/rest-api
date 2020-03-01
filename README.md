# Rest API

## Steps to install and use postgres:
1. `sudo apt-get install postgresql postgresql-contrib`
2. `sudo apt-get install libpq-dev python3-dev`
3. `pipenv install psycopg2` (inside to project terminal -> virtual environment)
4. Open Postgres Service:`sudo -u postgres -i`
5. Log in Postgres Database: `psql`
6. Create your user (with the username and password of your choice): `CREATE USER sample_user WITH PASSWORD 'sample_password';`
7. Create a new db and give the new user access:

    `CREATE DATABASE sample_database WITH OWNER sample_user;`
    
    `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sample_user;`