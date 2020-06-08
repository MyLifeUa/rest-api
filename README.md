# My Life Rest API

## Configuration

### Recommended Method: Docker Compose

The Django system is being packed in a docker image defined by the `Dockerfile` present in the root directory of this repository.

The best way of running the system, along with the postgres database needed, is by running the `docker-compose.yml` file, also available in the root directory of the repository.

```bash
docker-compose up [-d]
```

If you need to run any oher commands on a docker container, you can do:
```bash
docker-compose run <SERVICE_NAME> <COMMAND>
```
For example, if you want to run some tests on the django service, do:
```
docker-compose run django python manage.py test
```

Or, if you are getting an error when starting the server, the commando might not execute that way. Try:
```bash
docker-compose up -d
docker-compose exec <SERVICE> <COMMAND>
```
## Users Data

### Admins

| Username  | Password |
| ------------- | ------------- |
| antonio.martins@saojoao.pt  | letmein  |
| rui.almeida@santoantonio.pt  | qwerty  |
| pedro.silva@luz.pt  | ola  |

### Users 

| Username  | Password |
| ------------- | ------------- |
| vasco.almeida@gmail.com  | olaola  |
| ana.almeida@gmail.com  | olaolaola  |
| miguel.silva@gmail.com  | 12345ola  |
| miguel.oliveira@gmail.com | qwerty98765 |
| antonio.silva@gmail.com | 12345olaola |
| miguel.pedroseiro@gmail.com | pedrosorules |
| fatima.silva@gmail.com | qwertyola |
| laura.silva@gmail.com | 12345ola |
| pedro.pereira@gmail.com | pedropedro |
| miguel.pereira@gmail.com | 12345ola |
| manuela.silva@gmail.com | 12345ola |
| antonio.almeida@gmail.com | 12345ola |
| paulo.silva@gmail.com | 12345ola |
| andre.silva@gmail.com | 12345ola |
| miguel.matos@gmail.com | 12345ola |
| miguel.pedroso@gmail.com | 12345ola |
| alberto.matos@gmail.com | 12345ola |
| alberto.marques@gmail.com | 12345ola |
| agostinho.matos@gmail.com | 12345ola |
| albertina.matos@gmail.com | 12345ola |

### Doctors

| Username  | Password |
| ------------- | ------------- |
| andre.almeida@gmail.com  | qwerty12345  |
| rui.pereira@gmail.com  | asdfgh  |
| joao.pereira@gmail.com  | 987654  |


## Acknowledgments

* The barcode functionality was built using the REST API of: https://world.openfoodfacts.org/data
* The implementation of barcode functionality was done with the help of the repo available at: https://github.com/openfoodfacts/openfoodfacts-python
