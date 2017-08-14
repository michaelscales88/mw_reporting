FROM python:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install -U pip
RUN pip install --requirement /tmp/requirements.txt

# Define working directory
WORKDIR /app

COPY main.py .