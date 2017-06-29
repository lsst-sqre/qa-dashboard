# qa-dashboard

For SQuaSH development you can build a docker image 
or install the dependencies on a virtual environment following 
the instructions below.

## Building a docker image

```
  git clone  https://github.com/lsst-sqre/qa-dashboard.git
  make
  docker run -it -p 5006:5006 -p 8000:8000 lsstsqre/squash
```
Then access the application at http://localhost:8000 

## Using virtualenv

1. Clone the project, create a virtualenv and install dependencies
```
  git clone  https://github.com/lsst-sqre/qa-dashboard.git

  cd qa-dashboard

  virtualenv env -p python3
  source env/bin/activate
  pip install -r requirements.txt
```

2. Install MariaDB 10.1+

For example, using brew:
```
  brew install mariadb
  mysql.server start
```

3. Initialize the development database
```
  cd squash

  mysql -u root -e "DROP DATABASE qadb"
  mysql -u root -e "CREATE DATABASE qadb"

  python manage.py makemigrations
  python manage.py migrate

  # In this step django will ask for a "superuser" password, it is used to access the django admin interface

  export TEST_USER=root
  export TEST_USER_EMAIL="$TEST_USER@example.com"

  python manage.py createsuperuser --username $TEST_USER --email $TEST_USER_EMAIL
```
  
4. Execute tests (optional)
```
  python manage.py check
  python -Wi manage.py test dashboard.tests
```

5. Start the django application
```
  ./run.sh
```

6. On another terminal, load test data and start the bokeh server
```
  cd qa-dashboard

  source env/bin/activate
  cd squash
  python manage.py loaddata test_data
  ./bokeh.sh
```

Then access the application at http://localhost:8000

See also http://sqr-009.lsst.io/en/latest/
