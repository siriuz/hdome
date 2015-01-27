
# HDOME

A Django-powered engine for interrogation of immunoproteomic data

Requires postgres >= 9.3, Python2.7

For test data please contact kieranrimmer@gmail.com

Dependencies:

	- django-1.7b1
	- psycopg2
	- django_extensions
        - django-guardian
        - db_ops
        - requests
        - uniprot


Note to self, to plot db map:

	python manage.py graph_models <app_name> -g -o <output_file_name>.png

kieranrimmer@gmail.com
