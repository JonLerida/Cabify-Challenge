FROM python:3.7

WORKDIR /app
COPY . /app
COPY ./src app/src

EXPOSE 9091

ENTRYPOINT python3 ./src/server.py

