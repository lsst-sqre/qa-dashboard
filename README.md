# qa-dashboard

Cloning the project
```
  $ git clone  https://github.com/lsst-sqre/qa-dashboard.git
```

Create a virtualenv and install dependencies
```
  $ cd qa-dashboard
  $ virtualenv env -p python3
  $ source env/bin/activate
  $ pip install -r requirements.txt
```

Initialize the app in development mode:
```
  $ cd squash
  $ ./run.sh
```
the first time you will be asked to set a database password for your user.

Open another terminal to load test data for visualization and initialize the bokeh server.
```
  $ cd qa-dashboard
  $ source env/bin/activate
  $ cd squash
  $ python manage.py loaddata test_data
  $ ./bokeh.sh
```

Then access the application at http://localhost:8000

See also http://sqr-009.lsst.io/en/latest/
