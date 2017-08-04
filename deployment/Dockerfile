FROM tiangolo/uwsgi-nginx-flask:flask-python3.5
MAINTAINER Michael Scales "michael.scales@g.austincc.edu"

EXPOSE 8080

RUN mkdir ./app
WORKDIR .

COPY requirements.txt /app/requirements.txt

# upgrade pip and install required python packages
RUN pip install -U pip
RUN pip install -r /app/requirements.txt

COPY ./app/ app/
COPY main.py .

#CMD python3 main.py