FROM python:3.5

EXPOSE 8080

RUN mkdir /app
WORKDIR .

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY /app /app
COPY main.py .

CMD python main.py