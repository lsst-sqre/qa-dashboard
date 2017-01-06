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

2. Install MariaDB 10.1+ and create the development database

For example, using brew:
```
  brew install mariadb
  mysql.server start
```

3. Initialize the development database
```
  cd squash
  mysql -u root -e "DROP DATABASE squash"
  mysql -u root -e "CREATE DATABASE squash"

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

5.  In another terminal execute the tests for DM-8890
```
  cd qa-dashboard
  source env/bin/activate
  cd squash
  export TEST_USER=root
  export TEST_PASSWORD=<set to the passwd created in the previous step>
  py.test
```

For this particular ticket we are interested in checking the measurement API endpoint http://localhost:8000/dashboard/api/measurements/

See also http://sqr-009.lsst.io/en/latest/
