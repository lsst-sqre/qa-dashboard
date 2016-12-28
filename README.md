# qa-dashboard

1. Cloning the project
```
  git clone  https://github.com/lsst-sqre/qa-dashboard.git
```

Create a virtualenv and install dependencies
```
  cd qa-dashboard
  virtualenv env -p python3
  source env/bin/activate
  pip install -r requirements.txt
```

2. Install MySQL 5.7+ and create the development database

For example, using brew:
```
  brew install mysql
  mysql.server start
  mysql -u root -e "DROP DATABASE squash"
  mysql -u root -e "CREATE DATABASE squash"
```

3. Initialize the development database
```
  cd squash
  python manage.py makemigrations
  python manage.py migrate

  # In this step django will ask for a "superuser" password, it is used to access the django admin interface
  
  export TEST_USER=root
  export TEST_USER_EMAIL="$TEST_USER@example.com"

  python manage.py createsuperuser --username $TEST_USER --email $TEST_USER_EMAIL
```

4. Initialize the app in development mode:
```
  ./run.sh
```

5. On another terminal, load test data and initialize the bokeh server
```
  cd qa-dashboard
  source env/bin/activate
  cd squash
  python manage.py loaddata initial_data
  python manage.py loaddata test_data
  ./bokeh.sh
```

Then access the application at http://localhost:8000

See also http://sqr-009.lsst.io/en/latest/
