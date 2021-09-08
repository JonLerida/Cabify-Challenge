FROM python:3.7

WORKDIR /app
COPY . .
COPY ./src ./src

EXPOSE 9091

ENTRYPOINT ["python", "./src/server.py"]

