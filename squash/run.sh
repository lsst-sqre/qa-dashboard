#!/bin/bash
# Run dashboard app in development mode

if [ "$DJANGO_SETTINGS_MODULE" = "squash.settings.production" ];
then
    echo "Do not use this script in production mode."
    exit 1
fi
python manage.py runserver
