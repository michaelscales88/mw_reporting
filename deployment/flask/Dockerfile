FROM flask_base:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

ENV base_dir /var/www/
ENV app_dir /var/www/app/

RUN mkdir ${base_dir}
RUN mkdir ${app_dir}

# Actual code is mounted as a volume
COPY flask/uwsgi.ini ${app_dir}
COPY flask/wsgi.py ${app_dir}

# Set entrypoint directory
WORKDIR ${app_dir}
