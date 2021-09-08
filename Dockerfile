# syntax=docker/dockerfile:1
FROM python:3.7-alpine3.13

WORKDIR /app
COPY . .

EXPOSE 9091/tcp
CMD ["python3", "-u", "./src/server.py"]
