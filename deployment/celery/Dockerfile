FROM flask_base:latest
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

ENV DEBIAN_FRONTEND noninteractive
ENV ETCDCTL_VERSION v2.2.5
ENV DUMB_INIT_VERSION 1.0.1

# Install entrypoint
RUN apk add --no-cache --update \
        openssl \
        curl \
        ca-certificates \

    # Etcdctl
    && curl -L https://github.com/coreos/etcd/releases/download/$ETCDCTL_VERSION/etcd-$ETCDCTL_VERSION-linux-amd64.tar.gz -o /tmp/etcd-$ETCDCTL_VERSION-linux-amd64.tar.gz \
    && cd /tmp && gzip -dc etcd-$ETCDCTL_VERSION-linux-amd64.tar.gz | tar -xof -  \
    && cp -f /tmp/etcd-$ETCDCTL_VERSION-linux-amd64/etcdctl /usr/local/bin \

    # Dumb Init
    && wget -O /usr/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v${DUMB_INIT_VERSION}/dumb-init_${DUMB_INIT_VERSION}_amd64 \
    && chmod +x /usr/bin/dumb-init \

    # Cleanup
    && rm -rf /tmp/*

# Install python requirements
COPY requirements.txt /tmp/

RUN apk add --no-cache \
    --virtual=build_dependencies \
    postgresql-dev musl-dev linux-headers \
    gcc python3-dev make cmake g++ gfortran \

    && pip install -r /tmp/requirements.txt \

    # Remove build environment
    && apk del build_dependencies \

    # Cleanup
    && rm -rf /tmp/* \
    && rm -rf /root/.cache/pip/ \

#ADD celery.sh /var/opt/celery-flower/bin/
#RUN chmod +x /var/opt/celery-flower/bin/celery.sh
#
#WORKDIR /var/opt/celery-flower
#
EXPOSE 5555

#CMD ["/usr/bin/dumb-init", "/opt/celery-flower/bin/flower.sh"]

