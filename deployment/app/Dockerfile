FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies
COPY deployment/app/requirements.txt /tmp
RUN pip install -U pip
RUN pip install --requirement /tmp/requirements.txt

RUN mkdir /app
WORKDIR /app

COPY deployment/app/app.ini /app
COPY deployment/app/wsgi.py /app
