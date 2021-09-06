# syntax=docker/dockerfile:1
FROM python:3.7.4

WORKDIR /app
EXPOSE 60000/tcp
COPY . .
CMD ["python3", "-u", "server.py"]