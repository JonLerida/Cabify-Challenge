FROM python:latest

WORKDIR /app
COPY . .

EXPOSE 9091

ENTRYPOINT ["python3"]

#CMD ["python3", "-u", "./src/server.py"]
CMD ["./src/server.py"]
