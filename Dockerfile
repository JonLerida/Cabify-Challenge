FROM python:latest

WORKDIR /app
COPY . .

EXPOSE 9091

#CMD ["python3", "-u", "./src/server.py"]
CMD python3 ./src/server.py
