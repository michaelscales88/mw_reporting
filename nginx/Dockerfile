FROM connexiolabs/alpine-nginx:1.7.11
#RUN mkdir /etc/ssl/botillsammans
#COPY ./ssl/dhparams.pem /etc/ssl/botillsammans
#COPY ./ssl/botillsammans.klumpen.se /etc/ssl/botillsammans
#COPY ./sites-enabled /etc/nginx/sites-enabled
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params
CMD ["/usr/local/sbin/nginx", "-c", "/etc/nginx/nginx.conf"]