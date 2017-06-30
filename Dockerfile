# Docker image for squash development
FROM python:3.5

LABEL maintainer "afausti@lsst.org"

WORKDIR /usr/src/app

COPY . .

# squash dependencies
RUN pip install --no-cache-dir -r requirements.txt

# other dependencies required to run this image
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server mariadb-client supervisor \
    && mkdir -p /var/log/supervisor

WORKDIR /usr/src/app/squash

# Initialize squash development database
ENV user root

RUN /etc/init.d/mysql start \
    && mysql -u ${user} -e "CREATE DATABASE qadb" \
    && python -Wi manage.py makemigrations \
    && python -Wi manage.py migrate \
    && python -Wi manage.py createsuperuser --noinput --username ${user} --email root@example.com \
    && python -Wi manage.py loaddata test_data

# on the localhost django will run on port 8000 and bokeh on 5006
EXPOSE 8000 5006

# Start mysql, django and bokeh servers
CMD ["/usr/bin/supervisord", "-c", "supervisord.conf"]


