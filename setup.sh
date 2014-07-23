#! /bin/bash

# usage: sudo setup.sh <desired postgres password>


#ssh -i /home/rimmer/programs/keys/test_production_01.key ubuntu@118.138.241.207
sudo apt-get -y update;
sudo apt-get install -y nginx python-flup;
sudo apt-get install -y python-pip;
sudo apt-get install -y python-virtualenv;
sudo apt-get install -y git;
virtualenv hd_env;
sudo apt-get install -y postgresql postgresql-contrib;
#### postgres setup
sudo -u postgres createuser --superuser $SUDO_USER;
sudo -u postgres psql -c "ALTER USER $SUDO_USER WITH PASSWORD '$1';";
#sudo -u postgres psql postgres;
##inside postgres
#\password $USER # doesn't work
#\password ubuntu #
#f
#f
#d\q
##

createdb hdometwo;


source hd_env/bin/activate;
pip install https://www.djangoproject.com/download/1.7b1/tarball/;
pip install django-extensions;
pip install django-guardian;
pip install uniprot;
pip install gunicorn;
sudo apt-get update;
sudo apt-get install libpq-dev python-dev; # essential for instaling psycopg2
pip install psycopg2;
#sudo apt-get install python-psycopg2;
git clone https://github.com/kieranrimmer/hdome.git;
psql hdometwo < 140708_01.sql; # or whatever infile you like
sudo apt-get install screen;


sudo touch /etc/nginx/sites-available/sample_project.conf;
sudo ln -s /etc/nginx/sites-available/sample_project.conf /etc/nginx/sites-enabled/sample_project.conf;
sudo rm /etc/nginx/sites-enabled/default;

## add content to /etc/nginx/sites-available/sample_project.conf
## ensure /etc/nginx/nginx.conf is correct



#screen
gunicorn --timeout=90 --graceful-timeout=10 hdome.wsgi:application;
#exit screen
sudo service nginx restart;



