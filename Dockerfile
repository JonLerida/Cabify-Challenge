# syntax=docker/dockerfile:1
FROM python:3.7-alpine3.13

WORKDIR /app
COPY . .
COPY ./src .



EXPOSE 9091/tcp
CMD ["python3", "-u", "server.py"]


# WORKDIR /app/src
#CMD ["python3", "-u", "server.py"]
# docker build --tag cabify-python
# docker run -p 60000:60000 cabify-python
