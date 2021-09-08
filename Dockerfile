FROM python:3.7

WORKDIR /app

COPY . /app

EXPOSE 9091

ENTRYPOINT python3 ./src/server.py

