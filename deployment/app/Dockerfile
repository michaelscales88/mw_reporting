FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies
COPY deployment/app/requirements.txt /tmp/
RUN pip install -U pip
RUN pip install --requirement /tmp/requirements.txt

# Define working directory
WORKDIR /app

COPY deployment/app/app.ini /app
COPY wsgi.py .