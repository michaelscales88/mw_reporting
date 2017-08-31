FROM python:3.6-alpine

ENV PANDAS_VERSION 0.18.1

# Long installation components in base image
RUN apk add --no-cache \
    --virtual=build_dependencies \
    musl-dev gcc python3-dev make cmake g++ gfortran \

    # Header files to build numpy and pandas
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install numpy \
    && pip install pandas==${PANDAS_VERSION} \
    && apk del build_dependencies \
    && apk add --no-cache libstdc++ \
    && rm -rf /var/cache/apk/*
