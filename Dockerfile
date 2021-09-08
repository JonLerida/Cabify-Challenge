FROM python:3.7-alpine3.13

WORKDIR /app
COPY . .

EXPOSE 9091

CMD ["python3", "-u", "./src/server.py"]
