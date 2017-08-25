FROM nginx
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

ENV work_dir /etc/nginx

# Install dependencies
COPY nginx/sites-available/ ${work_dir}/sites-enabled/
COPY nginx/nginx.conf ${work_dir}
COPY nginx/uwsgi_params ${work_dir}
COPY nginx/.htpasswd ${work_dir}

# Set entrypoint directory
WORKDIR ${work_dir}