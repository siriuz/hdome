#!/bin/bash

NAME="hdome"                                  # Name of the application
VENVDIR=/home/rimmer/hdome/env                 # virtualenv directory
DJANGODIR=/home/rimmer/praccie/hdome             # Django project directory
SOCKFILE=/home/rimmer/praccie/hdome/run/gunicorn.sock  # we will communicte using this unix socket
USER=rimmer                                        # the user to run as
GROUP=rimmer                                     # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=hdome.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=hdome.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $VENVDIR
source bin/activate
cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $VENVDIR/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-
