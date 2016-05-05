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

See also http://sqr-009.lsst.io/en/latest/
