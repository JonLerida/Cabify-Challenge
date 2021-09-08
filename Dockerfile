FROM python:latest

WORKDIR /app
COPY . .

EXPOSE 9091

ENTRYPOINT ["python3", "./src/server.py"]

