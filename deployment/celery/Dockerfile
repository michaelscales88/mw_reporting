FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"


# Install dependencies
COPY deployment/flask/requirements.txt /var/tmp/
RUN pip install -U pip
RUN pip install --requirement /var/tmp/requirements.txt

WORKDIR /var/www/app