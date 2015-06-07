INSTALLING AND RUNNING PASTEBIN-DJANGO
===
These steps explain how to get pastebin-django working in such a way that it can be launched using the provided manage.py script (which is unsuitable for production use!), the database connection works correctly, etc. There are multiple ways to run Django projects in a production environment, although for pastesite.matoking.com I've used uWSGI with nginx. Instructions for running a Django application with that stack can be found here:
https://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html


Installing dependencies
--
pastebin-django requires Python and a few related dependencies to be installed (virtualenv, pip). The following command should install the required dependencies if you are running on Debian or a derivative (eg. Linux Mint, Ubuntu).

sudo apt-get install python python-dev python-pip python-virtualenv

Creating virtualenv container and installing required Python libraries
--
Although this step is optional, it's recommended to install and run the web application inside a virtualenv environment, as this isolates the web application's environment from the system-wide Python installation, thus ensuring that your web application won't be accidentally broken by a system-wide update.

To create the virtualenv environment, run the following command on the pastebin-django directory, which contains the project's apps such as pastes, comments.

virtualenv pastebin-django

Once you have created the virtualenv environment, you can start using it by running the following command.

source bin/activate

You can always deactivate the virtualenv environment by running the following command.

deactivate

But instead of leaving the environment, let's install the required Python libraries using pip. cd inside the pastebin-django directory and install the required Python libraries. Note that sudo isn't necessary, as we are installing all of the libraries inside our isolated Python environment.

cd pastebin-django
pip install -r requirements.txt

Configuring the PostgreSQL database
--
We'll assume you have already created a database and a role which can access the said database. Start by opening the settings.py file in pastebin/settings.py and changing the credentials in DATABASES['default']. If you're going to be running unit tests, you can change the database name in DATABASES['default']['TEST']['NAME'], which is the database that will be used when running the unit tests.

After this is done, run the following command in the root of your virtualenv environment to create Django's in-built database tables. You may also be prompted to create a superuser, which you can use when logging into pastebin-django.

python manage.py syncdb

Configuring the Redis instance
--
pastebin-django uses a data structure server to both to store persistent data that wouldn't be a good fit for a relational database (eg. paste hit counts). You can install Redis on Debian or a derivative using the following command.

sudo apt-get install redis-server

By default Redis runs on port 6379 and saves its data regularly. However, pastebin-django's default settings assume a persistent Redis storage runs on the port 6380, so you may need to change the port for the 'persistent' cache in settings.py to match this port. You can also run a non-persistent Redis server under the port 6379 and a persistent Redis server under port 6380, which matches the default settings. 

Running the unit tests
--
At this point your web application should be configured correctly. But to make sure that everything will work nicely before we try running the web application, run the unit tests using the following command. You can use your "normal" database when running the unit tests, but you'll need to recreate the tables described in sql/create_tables.sql after running the tests, as those will be automatically dropped.

python manage.py test

If everything worked as intended, all of the tests should pass which means the web application <--> database connection is working correctly.

Starting the development web server
--
We are now ready to start the development web server. Run the following command to run the web application on 127.0.0.1:8000, which is also the URL you'll need to enter into your web browser in order to access the site. Feel free to change the address and/or port depending on your working environment.

python manage.py runserver 127.0.0.1:8000

Now, try opening http://127.0.0.1:8000 in your web browser. If everything worked out correctly, you should now be able to use the web application as normal.
