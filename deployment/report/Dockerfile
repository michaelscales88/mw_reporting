FROM tiangolo/uwsgi-nginx-flask:flask-python3.5
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Define working directory
WORKDIR /app

COPY main.py .

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install -U pip
RUN pip install --requirement /tmp/requirements.txt