FROM ubuntu:trusty
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

RUN apt-get -y update && apt-get -y install python-dev python-pip

RUN pip install flower

# Set entrypoint directory
WORKDIR /var/www/app