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

The dashboard application will run on port 8000.

Open another terminal and start the bokeh server:
```
  $ ./bokeh.sh
```
Run the tests to get some data for visualization, it uses the API to post test jobs each 5 seconds. Set the variable `TEST_PASSWD` to the same password used to set up the database.

```
  $ export TEST_PASSWD='<same databse password as above>'
  $ py.test
```

See also http://sqr-009.lsst.io/en/latest/
