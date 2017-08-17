FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"


# Install dependencies
COPY deployment/flask/requirements.txt /var/tmp/
RUN pip install -U pip
RUN pip install --requirement /var/tmp/requirements.txt

RUN mkdir /var/www/
RUN mkdir /var/www/app/

# Actual code is mounted as a volume
COPY deployment/flask/uwsgi.ini /var/www/app/
COPY deployment/flask/wsgi.py /var/www/app/

# Set entrypoint directory
WORKDIR /var/www/app
