FROM nginx
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

# Install dependencies
COPY deployment/nginx/sites-available/flask.conf /etc/nginx/sites-enabled/
COPY deployment/nginx/nginx.conf /etc/nginx/
COPY deployment/nginx/uwsgi_params /etc/nginx/

# Set entrypoint directory
WORKDIR /etc/nginx